"""Read-only chunked EDA runner for LendingClub accepted-loan data."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from visualization.eda_plots import bar_chart, heatmap, histogram, line_chart

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "accepted_2007_to_2018Q4.csv"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
USECOLS = ["id","loan_amnt","funded_amnt","int_rate","grade","sub_grade","emp_length","home_ownership","annual_inc","verification_status","issue_d","loan_status","purpose","addr_state","dti","fico_range_low","fico_range_high","revol_util","revol_bal","term"]
CATS = ["loan_status","grade","sub_grade","purpose","emp_length","home_ownership","verification_status","addr_state"]
NUMS = ["loan_amnt","funded_amnt","int_rate","annual_inc","dti","fico_range_low","fico_range_high","revol_util","revol_bal"]
RISK_BINS = {"int_rate": ([0, 8, 12, 16, 20, 100], ["<8%", "8–12%", "12–16%", "16–20%", "20%+"]), "annual_inc": ([0, 40000, 60000, 80000, 120000, np.inf], ["<40k", "40–60k", "60–80k", "80–120k", "120k+"]), "dti": ([0, 10, 20, 30, 40, np.inf], ["<10", "10–20", "20–30", "30–40", "40+"]), "revol_util": ([0, 25, 50, 75, 100, np.inf], ["<25%", "25–50%", "50–75%", "75–100%", "100%+"]), "fico_mid": ([0, 660, 700, 740, 780, np.inf], ["<660", "660–699", "700–739", "740–779", "780+"])}

def number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce")

def default_flag(status: pd.Series) -> pd.Series:
    return status.astype(str).str.strip().str.lower().isin(["charged off", "default"]).astype(int)

def kendall_tau_a(frame: pd.DataFrame, maximum_rows: int = 600) -> pd.DataFrame:
    """Compute a deterministic rank-correlation approximation without SciPy."""
    data = frame.iloc[:maximum_rows].to_numpy(dtype=float)
    result = np.eye(data.shape[1])
    for i in range(data.shape[1]):
        for j in range(i + 1, data.shape[1]):
            x, y = data[:, i], data[:, j]
            dx = np.sign(x[:, None] - x[None, :]); dy = np.sign(y[:, None] - y[None, :])
            upper = np.triu(np.ones_like(dx, dtype=bool), 1)
            comparable = upper & (dx != 0) & (dy != 0)
            value = float((dx[comparable] * dy[comparable]).sum() / max(comparable.sum(), 1))
            result[i, j] = result[j, i] = value
    return pd.DataFrame(result, index=frame.columns, columns=frame.columns)

def run() -> dict:
    if not RAW.is_file(): raise FileNotFoundError(RAW)
    total_rows=0; total_funded=total_loan=0.0; num_sums=Counter(); num_counts=Counter(); status=Counter(); cat=defaultdict(Counter); cat_n=defaultdict(Counter); cat_loan=defaultdict(Counter); cat_inc=defaultdict(Counter); risk=defaultdict(Counter); risk_n=defaultdict(Counter); time_n=Counter(); time_default=Counter(); time_rate=Counter(); time_rate_n=Counter(); month_n=Counter(); missing=Counter(); dtype_observed={}; corr_rows=[]; sample=[]
    for chunk in pd.read_csv(RAW, usecols=USECOLS, chunksize=100_000, low_memory=False):
        total_rows += len(chunk)
        for column in chunk.columns: missing[column] += int(chunk[column].isna().sum()); dtype_observed[column]=str(chunk[column].dtype)
        for column in ["int_rate","revol_util",*NUMS]:
            if column in chunk: chunk[column]=number(chunk[column])
        chunk["default"] = default_flag(chunk["loan_status"])
        chunk["fico_mid"] = (chunk["fico_range_low"]+chunk["fico_range_high"])/2
        total_funded += chunk["funded_amnt"].sum(skipna=True); total_loan += chunk["loan_amnt"].sum(skipna=True)
        for column in ["loan_amnt","int_rate","annual_inc","dti","fico_mid","revol_util"]:
            values=chunk[column].dropna(); num_sums[column]+=float(values.sum()); num_counts[column]+=int(values.count())
        status.update(chunk["loan_status"].fillna("Missing").astype(str))
        for column in CATS:
            group=chunk[column].fillna("Missing").astype(str)
            cat_n[column].update(group)
            cat[column].update(chunk["default"].groupby(group).sum().to_dict())
            cat_loan[column].update(chunk["loan_amnt"].groupby(group).sum().to_dict())
            cat_inc[column].update(chunk["annual_inc"].groupby(group).sum().to_dict())
        for column, (edges, labels) in RISK_BINS.items():
            group = pd.Series(pd.cut(chunk[column], bins=edges, labels=labels, include_lowest=True), index=chunk.index).astype(object).where(lambda x: x.notna(), "Missing").astype(str)
            risk_n[column].update(group)
            risk[column].update(chunk["default"].groupby(group).sum().to_dict())
        dates=pd.to_datetime(chunk["issue_d"],format="%b-%Y",errors="coerce"); period=dates.dt.to_period("Q").astype(str)
        month_n.update(dates.dt.month_name().dropna())
        for key, part in chunk.assign(period=period).dropna(subset=["period"]).groupby("period"):
            time_n[key]+=len(part); time_default[key]+=int(part["default"].sum()); time_rate[key]+=float(part["int_rate"].sum(skipna=True)); time_rate_n[key]+=int(part["int_rate"].count())
        corr_rows.append(chunk[["loan_amnt","int_rate","annual_inc","dti","fico_mid","revol_util","default"]].sample(min(1000,len(chunk)),random_state=42))
        if len(sample)<10000: sample.append(chunk.sample(min(2000,len(chunk)),random_state=7))
    averages={k: num_sums[k]/num_counts[k] for k in num_sums}; profile={c:{"missing_count":missing[c],"missing_pct":round(100*missing[c]/total_rows,3),"dtype":dtype_observed[c]} for c in USECOLS}
    def grouped(column, limit=30):
        result=[]
        for key,count in cat_n[column].most_common(limit): result.append({"category":key,"loans":count,"default_rate":round(100*cat[column][key]/count,3),"avg_loan_amount":round(cat_loan[column][key]/count,2),"avg_income":round(cat_inc[column][key]/count,2)})
        return result
    def binned(column): return [{"band":key,"loans":count,"default_rate":round(100*risk[column][key]/count,3)} for key,count in risk_n[column].items()]
    summary={"source_file":RAW.name,"rows":total_rows,"columns":len(USECOLS),"file_size_bytes":RAW.stat().st_size,"totals":{"funded_amount":total_funded,"loan_amount":total_loan},"averages":averages,"loan_status":dict(status),"groups":{c:grouped(c) for c in CATS},"risk_bands":{c:binned(c) for c in RISK_BINS},"data_quality":profile}
    corr=pd.concat(corr_rows,ignore_index=True).dropna()
    correlations={"pearson":corr.corr(method="pearson").round(4).to_dict(),"spearman":corr.corr(method="spearman").round(4).to_dict(),"kendall":kendall_tau_a(corr).round(4).to_dict()}
    summary["correlations"]=correlations
    REPORTS.mkdir(exist_ok=True); FIGURES.mkdir(exist_ok=True)
    bar_chart(FIGURES/"loan_status_distribution.svg",*zip(*status.most_common()),"Loan status distribution",subtitle="Observed servicing status; not a matured-cohort default rate.",value_format=",.0f")
    for column,title in [("grade","Grade distribution"),("sub_grade","Sub-grade distribution"),("purpose","Loan purpose distribution"),("emp_length","Employment length distribution"),("home_ownership","Home ownership distribution")]:
        rows=grouped(column,35); bar_chart(FIGURES/f"{column}_distribution.svg",[r["category"] for r in rows],[r["loans"] for r in rows],title,subtitle="Loan count",value_format=",.0f")
        risk=sorted(rows,key=lambda x:x["default_rate"],reverse=True); bar_chart(FIGURES/f"{column}_default_rate.svg",[r["category"] for r in risk],[r["default_rate"] for r in risk],f"Observed default rate by {column.replace('_',' ')}",subtitle="Charged Off or Default / all originated loans; interpret with vintage mix.",value_format=".2f",color="#B33A3A")
    for column, rows in summary["risk_bands"].items():
        bar_chart(FIGURES/f"{column}_band_default_rate.svg",[r["band"] for r in rows],[r["default_rate"] for r in rows],f"Observed default rate by {column.replace('_',' ')} band",subtitle="Analytical bands for portfolio monitoring, not feature engineering.",value_format=".2f",color="#B33A3A")
    periods=sorted(time_n); line_chart(FIGURES/"time_trends.svg",periods,{"Originations": [time_n[p] for p in periods],"Default rate (%)": [100*time_default[p]/time_n[p] for p in periods],"Average interest rate (%)": [time_rate[p]/time_rate_n[p] for p in periods]},"Portfolio growth, default and rate trends",subtitle="Quarterly originations, unconditional default rate, and average coupon; axes are shared for directional comparison.")
    bar_chart(FIGURES/"loans_by_month.svg",list(month_n),[month_n[key] for key in month_n],"Loans issued by calendar month",subtitle="All years combined; seasonality requires vintage adjustment.",value_format=",.0f",horizontal=False)
    labels=["loan_amnt","int_rate","annual_inc","dti","fico_mid","revol_util","default"]
    for method, matrix in correlations.items(): heatmap(FIGURES/f"correlation_{method}.svg",labels,np.array([[matrix[a][b] for b in labels] for a in labels]),f"{method.title()} correlation heatmap")
    numeric_sample=corr_rows[0] if corr_rows else pd.DataFrame()
    for column,label in [("loan_amnt","Loan amount"),("int_rate","Interest rate (%)"),("annual_inc","Annual income"),("dti","Debt-to-income ratio"),("fico_mid","FICO midpoint"),("revol_util","Revolving utilisation (%)")]:
        values=corr[column].to_numpy(); values=values[np.isfinite(values)];
        if len(values): histogram(FIGURES/f"distribution_{column}.svg",values,f"Distribution — {label}",x_label=label)
    summary["time_series"]=[{"period":p,"loans":time_n[p],"default_rate":round(100*time_default[p]/time_n[p],3),"avg_interest_rate":round(time_rate[p]/time_rate_n[p],3)} for p in periods]
    (REPORTS/"eda_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    return summary

if __name__ == "__main__":
    output=run(); print(json.dumps({"rows":output["rows"],"figures":len(list(FIGURES.glob("*.svg")))},indent=2))
