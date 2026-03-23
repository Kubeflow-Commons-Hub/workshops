#!/usr/bin/env python3
"""Minimal PyTorch CPU trainer for the fraud workshop (tabular)."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn

DATA_CSV = Path(os.environ.get("WORKSHOP_DATA", "/workspace/data/transactions.csv"))
OUT_DIR = Path(os.environ.get("WORKSHOP_OUT", "/workspace/out"))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_CSV.is_file():
        raise SystemExit(f"Missing data file: {DATA_CSV}")

    df = pd.read_csv(DATA_CSV)
    feature_cols = [c for c in df.columns if c not in ("user_id", "event_timestamp", "is_fraud")]
    if not feature_cols:
        feature_cols = ["amount"]

    x = torch.tensor(df[feature_cols].values, dtype=torch.float32)
    y = torch.tensor(df["is_fraud"].values, dtype=torch.float32).unsqueeze(1)

    class Net(nn.Module):
        def __init__(self, n: int) -> None:
            super().__init__()
            self.lin = nn.Linear(n, 1)

        def forward(self, t: torch.Tensor) -> torch.Tensor:
            return torch.sigmoid(self.lin(t))

    model = Net(len(feature_cols))
    opt = torch.optim.Adam(model.parameters(), lr=0.15)
    loss_fn = nn.BCELoss()

    for _ in range(300):
        opt.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        opt.step()

    out_path = OUT_DIR / "model.pt"
    torch.save({"state_dict": model.state_dict(), "feature_cols": feature_cols}, out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
