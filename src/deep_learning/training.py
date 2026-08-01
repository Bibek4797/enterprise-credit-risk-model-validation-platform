"""PyTorch MLP Training Engine with Early Stopping, LR Scheduling, and Performance Profiling."""

from __future__ import annotations

import logging
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
from deep_learning.mlp import CreditRiskMLP

logger = logging.getLogger(__name__)


def train_credit_mlp(
    X_train: pd.DataFrame | np.ndarray,
    y_train: pd.Series | np.ndarray,
    X_val: pd.DataFrame | np.ndarray,
    y_val: pd.Series | np.ndarray,
    epochs: int = 40,
    batch_size: int = 256,
    lr: float = 0.001,
    patience: int = 8,
) -> dict[str, object]:
    """Train PyTorch CreditRiskMLP classifier with early stopping and latency tracking."""
    # Scaling
    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    X_tr_t = torch.tensor(X_tr_scaled, dtype=torch.float32)
    y_tr_t = torch.tensor(np.asarray(y_train), dtype=torch.float32).unsqueeze(1)

    X_v_t = torch.tensor(X_val_scaled, dtype=torch.float32)
    y_v_t = torch.tensor(np.asarray(y_val), dtype=torch.float32).unsqueeze(1)

    train_ds = TensorDataset(X_tr_t, y_tr_t)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    input_dim = X_tr_scaled.shape[1]
    model = CreditRiskMLP(input_dim=input_dim, hidden_dims=[128, 64, 32], dropout_rate=0.2)

    criterion = nn.BCELoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3)

    train_losses = []
    val_losses = []

    best_val_loss = float("inf")
    best_model_weights = None
    patience_counter = 0

    start_time = time.time()

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0

        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            out = model(batch_x)
            loss = criterion(out, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(batch_x)

        epoch_loss /= len(X_tr_scaled)
        train_losses.append(epoch_loss)

        # Validation phase
        model.eval()
        with torch.no_grad():
            v_out = model(X_v_t)
            v_loss = criterion(v_out, y_v_t).item()
            val_losses.append(v_loss)

        scheduler.step(v_loss)

        if v_loss < best_val_loss:
            best_val_loss = v_loss
            best_model_weights = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1

        if patience_counter >= patience:
            logger.info(f"Early stopping triggered at epoch {epoch + 1}")
            break

    training_duration = time.time() - start_time

    # Load best weights
    if best_model_weights is not None:
        model.load_state_dict(best_model_weights)

    # Inference latency benchmark
    model.eval()
    inf_start = time.time()
    with torch.no_grad():
        _ = model(X_v_t[:1000])
    inf_latency_ms = (time.time() - inf_start) * 1000.0

    def predict_proba_fn(X_new: pd.DataFrame | np.ndarray) -> np.ndarray:
        model.eval()
        X_scaled = scaler.transform(X_new)
        with torch.no_grad():
            preds = model(torch.tensor(X_scaled, dtype=torch.float32)).numpy().ravel()
        return preds

    return {
        "model": model,
        "scaler": scaler,
        "predict_proba": predict_proba_fn,
        "training_duration_seconds": round(training_duration, 2),
        "inference_latency_1k_ms": round(inf_latency_ms, 2),
        "best_val_loss": round(best_val_loss, 5),
        "epochs_trained": len(train_losses),
        "train_loss_history": train_losses,
        "val_loss_history": val_losses,
    }
