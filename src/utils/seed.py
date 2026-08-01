"""Deterministic Random Seed Controller for Reproducibility."""

from __future__ import annotations

import os
import random
import numpy as np


def set_global_seed(seed: int = 42) -> None:
    """Set global random seed across Python, NumPy, and PyTorch for deterministic execution."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass
