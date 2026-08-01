"""Banking-grade multi-stage Feature Selection Framework.

Combines statistical evidence, business reasoning, multicollinearity screening,
LASSO regularization, RFE, stability filters, and model governance rules (SR 11-7 / Basel III).
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy.stats import spearmanr
from sklearn.feature_selection import (
    SelectKBest,
    VarianceThreshold,
    chi2,
    f_classif,
    mutual_info_classif,
)
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.feature_selection import RFECV
from statsmodels.stats.outliers_influence import variance_inflation_factor

from utils.helpers import LEAKAGE_PATTERNS

logger = logging.getLogger(__name__)


def missing_value_filter(
    df: pd.DataFrame,
    features: list[str],
    max_missing_pct: float = 0.50,
) -> tuple[list[str], pd.DataFrame]:
    """Screen out features exceeding maximum missingness threshold while logging business audit trail."""
    missing_pct = df[features].isnull().mean()
    audit_df = pd.DataFrame({
        "feature": features,
        "missing_pct": missing_pct.values,
        "action": np.where(missing_pct.values > max_missing_pct, "REMOVE", "KEEP"),
        "reason": np.where(missing_pct.values > max_missing_pct, f"Missing % exceeds threshold ({max_missing_pct*100:.1f}%)", "Passes missingness threshold"),
    })
    retained_features = audit_df[audit_df["action"] == "KEEP"]["feature"].tolist()
    return retained_features, audit_df


def correlation_clustering_filter(
    df: pd.DataFrame,
    features: list[str],
    threshold: float = 0.70,
    method: str = "spearman",
) -> tuple[list[str], pd.DataFrame, dict[int, list[str]]]:
    """Perform hierarchical linkage clustering on correlation matrix to reduce collinear redundancy."""
    numeric_df = df[features].select_dtypes(include=[np.number]).dropna()
    if numeric_df.empty or len(numeric_df.columns) <= 1:
        return features, pd.DataFrame(), {}

    if method == "spearman":
        corr_matrix = numeric_df.corr(method="spearman").abs()
    elif method == "kendall":
        corr_matrix = numeric_df.corr(method="kendall").abs()
    else:
        corr_matrix = numeric_df.corr(method="pearson").abs()

    # Fill NaN correlations with 0
    corr_matrix = corr_matrix.fillna(0.0)

    # Ward distance clustering
    distance_matrix = 1.0 - corr_matrix.values
    np.fill_diagonal(distance_matrix, 0)
    linkage = hierarchy.ward(hierarchy.distance.squareform(distance_matrix, checks=False))
    cluster_labels = hierarchy.fcluster(linkage, 1.0 - threshold, criterion="distance")

    clusters: dict[int, list[str]] = {}
    for feat, cid in zip(numeric_df.columns, cluster_labels):
        clusters.setdefault(cid, []).append(feat)

    retained_features = []
    cluster_records = []

    for cid, members in clusters.items():
        # Select representative with lowest overall mean correlation to others
        if len(members) == 1:
            best_feat = members[0]
        else:
            sub_corr = corr_matrix.loc[members, members]
            best_feat = sub_corr.mean(axis=1).idxmin()

        retained_features.append(best_feat)
        for member in members:
            cluster_records.append({
                "cluster_id": cid,
                "feature": member,
                "selected_representative": best_feat,
                "action": "KEEP" if member == best_feat else "REMOVE (Redundant)",
                "reason": f"Cluster {cid} correlated at > {threshold} threshold",
            })

    # Keep non-numeric features as well
    non_numeric = [f for f in features if f not in numeric_df.columns]
    retained_features.extend(non_numeric)

    audit_df = pd.DataFrame(cluster_records)
    return retained_features, audit_df, clusters


def multicollinearity_vif_filter(
    df: pd.DataFrame,
    features: list[str],
    max_vif: float = 5.0,
) -> tuple[list[str], pd.DataFrame]:
    """Iteratively remove features with high Variance Inflation Factor (VIF)."""
    numeric_df = df[features].select_dtypes(include=[np.number]).dropna()
    if numeric_df.empty or len(numeric_df.columns) <= 1:
        return features, pd.DataFrame()

    current_features = list(numeric_df.columns)
    vif_records = []

    while True:
        if len(current_features) <= 1:
            break
        vif_data = [
            variance_inflation_factor(numeric_df[current_features].values, i)
            for i in range(len(current_features))
        ]
        max_idx = np.argmax(vif_data)
        highest_vif = vif_data[max_idx]

        if highest_vif > max_vif:
            removed_feat = current_features.pop(max_idx)
            vif_records.append({
                "feature": removed_feat,
                "vif": float(highest_vif),
                "tolerance": float(1.0 / highest_vif),
                "action": "REMOVE",
                "reason": f"VIF {highest_vif:.2f} > max threshold {max_vif}",
            })
        else:
            for feat, vif_val in zip(current_features, vif_data):
                vif_records.append({
                    "feature": feat,
                    "vif": float(vif_val),
                    "tolerance": float(1.0 / vif_val) if vif_val > 0 else 1.0,
                    "action": "KEEP",
                    "reason": "VIF below threshold",
                })
            break

    retained_features = current_features + [f for f in features if f not in numeric_df.columns]
    audit_df = pd.DataFrame(vif_records).drop_duplicates(subset=["feature"], keep="last")
    return retained_features, audit_df


def compute_univariate_importance(
    df: pd.DataFrame,
    features: list[str],
    target: str = "target",
) -> pd.DataFrame:
    """Compute Mutual Information, ANOVA F-stat, Variance, and Univariate Logistic Regression AUC."""
    valid = df[features + [target]].dropna().copy()
    X = valid[features].select_dtypes(include=[np.number])
    y = valid[target].astype(int)

    if X.empty:
        return pd.DataFrame()

    # Variance
    variances = X.var()

    # Mutual Information
    mi_scores = mutual_info_classif(X, y, random_state=42)

    # ANOVA F-test
    f_stat, p_val = f_classif(X, y)

    # Univariate Logistic Regression AUC
    auc_scores = []
    for col in X.columns:
        try:
            clf = LogisticRegression(solver="lbfgs", max_iter=200)
            clf.fit(X[[col]], y)
            preds = clf.predict_proba(X[[col]])[:, 1]
            from sklearn.metrics import roc_auc_score
            auc_scores.append(roc_auc_score(y, preds))
        except Exception:
            auc_scores.append(0.50)

    summary_df = pd.DataFrame({
        "feature": X.columns,
        "variance": variances.values,
        "mutual_info": mi_scores,
        "anova_f_stat": f_stat,
        "anova_p_value": p_val,
        "univariate_auc": auc_scores,
    }).sort_values("mutual_info", ascending=False).reset_index(drop=True)

    return summary_df


def lasso_feature_selection(
    df: pd.DataFrame,
    features: list[str],
    target: str = "target",
    cv: int = 5,
) -> tuple[list[str], pd.DataFrame]:
    """Perform L1 (LASSO) logistic regression feature selection using cross-validation."""
    valid = df[features + [target]].dropna().copy()
    X = valid[features].select_dtypes(include=[np.number])
    y = valid[target].astype(int)

    if X.empty:
        return features, pd.DataFrame()

    # Standardize for LASSO scale invariance
    X_scaled = (X - X.mean()) / (X.std() + 1e-8)

    lasso_cv = LogisticRegressionCV(
        Cs=10,
        cv=cv,
        penalty="l1",
        solver="saga",
        max_iter=500,
        random_state=42,
        n_jobs=-1,
    )
    lasso_cv.fit(X_scaled, y)

    coefs = lasso_cv.coef_[0]
    audit_df = pd.DataFrame({
        "feature": X.columns,
        "lasso_coefficient": coefs,
        "abs_coefficient": np.abs(coefs),
        "selected": coefs != 0,
        "action": np.where(coefs != 0, "KEEP", "REMOVE (Shrunk to 0)"),
    }).sort_values("abs_coefficient", ascending=False).reset_index(drop=True)

    selected_features = audit_df[audit_df["selected"]]["feature"].tolist()
    return selected_features, audit_df


def rfe_feature_selection(
    df: pd.DataFrame,
    features: list[str],
    target: str = "target",
    n_features_to_select: int = 15,
    step: int = 1,
) -> tuple[list[str], pd.DataFrame]:
    """Perform Recursive Feature Elimination (RFECV) with Logistic Regression."""
    valid = df[features + [target]].dropna().copy()
    X = valid[features].select_dtypes(include=[np.number])
    y = valid[target].astype(int)

    if X.empty:
        return features, pd.DataFrame()

    estimator = LogisticRegression(solver="lbfgs", max_iter=200, random_state=42)
    rfecv = RFECV(
        estimator=estimator,
        step=step,
        cv=3,
        scoring="roc_auc",
        min_features_to_select=min(n_features_to_select, len(X.columns)),
        n_jobs=-1,
    )
    rfecv.fit(X, y)

    audit_df = pd.DataFrame({
        "feature": X.columns,
        "rfe_rank": rfecv.ranking_,
        "selected": rfecv.support_,
        "action": np.where(rfecv.support_, "KEEP", f"REMOVE (Rank {rfecv.ranking_})"),
    }).sort_values("rfe_rank").reset_index(drop=True)

    selected_features = audit_df[audit_df["selected"]]["feature"].tolist()
    return selected_features, audit_df
