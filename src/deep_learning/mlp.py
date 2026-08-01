"""PyTorch Multilayer Perceptron (MLP) Architecture for Credit Risk Default Prediction."""

from __future__ import annotations

import logging
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class CreditRiskMLP(nn.Module):
    """Production-grade PyTorch Multilayer Perceptron (MLP) Classifier."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: list[int] | None = None,
        dropout_rate: float = 0.2,
        use_batch_norm: bool = True,
    ) -> None:
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [128, 64, 32]

        layers = []
        in_dim = input_dim

        for h_dim in hidden_dims:
            layers.append(nn.Linear(in_dim, h_dim))
            if use_batch_norm:
                layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.LeakyReLU(0.1))
            if dropout_rate > 0.0:
                layers.append(nn.Dropout(dropout_rate))
            in_dim = h_dim

        # Final Sigmoid output layer for binary probability
        layers.append(nn.Linear(in_dim, 1))
        layers.append(nn.Sigmoid())

        self.model = nn.Sequential(*layers)
        self._init_weights()

    def _init_weights(self) -> None:
        """Initialize linear weights using Xavier Normalization."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass generating default probability P(y=1|x)."""
        return self.model(x)
