# data/dataset_loader.py - Load & align the ETH2 validators CSV to the environment schema

import os
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "validator_index",
    "slashed",
    "effective_balance_gwei",
    "attestations_total",
    "att_missed_total",
    "proposals_total",
    "prop_missed_total",
]

DERIVED_COLUMNS = [
    "stake",           # [0,1] normalized from effective_balance_gwei
    "uptime",          # [0,1] from attestations
    "missed_att",      # int
    "missed_prop",     # int
]

class DatasetLoader:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = None

    def load(self) -> pd.DataFrame:
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")

        if self.dataset_path.endswith(".csv"):
            df = pd.read_csv(self.dataset_path)
        elif self.dataset_path.endswith(".json"):
            df = pd.read_json(self.dataset_path, lines=False)
        else:
            raise ValueError("Unsupported dataset format. Provide CSV or JSON.")

        self.data = self._align(df)
        return self.data

    def _align(self, df: pd.DataFrame) -> pd.DataFrame:
        # Ensure required columns exist
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = np.nan

        # Sanitize numeric columns
        for col in ["effective_balance_gwei","attestations_total","att_missed_total","proposals_total","prop_missed_total"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Fill NaNs with sensible defaults
        def normalize_slashed(val):
            if pd.isna(val):
                return False
            if isinstance(val, (int, float)):
                return val != 0
            if isinstance(val, str):
                sval = val.strip().lower()
                if sval in {"true", "1", "yes", "y"}:
                    return True
                if sval in {"false", "0", "no", "n", ""}:
                    return False
                try:
                    return float(sval) != 0
                except Exception:
                    return False
            return bool(val)

        df["slashed"] = df.get("slashed", pd.NA).map(normalize_slashed).fillna(False).astype(bool)
        df["attestations_total"] = df["attestations_total"].fillna(0)
        df["att_missed_total"] = df["att_missed_total"].fillna(0)
        df["proposals_total"] = df["proposals_total"].fillna(0)
        df["prop_missed_total"] = df["prop_missed_total"].fillna(0)
        df["effective_balance_gwei"] = df["effective_balance_gwei"].fillna(0)

        # Derive features
        # stake normalized to [0,1] with cap at 32 ETH = 32e9 gwei
        CAP_GWEI = 32_000_000_000
        eff = df["effective_balance_gwei"].clip(lower=0, upper=CAP_GWEI)
        df["stake"] = (eff / float(CAP_GWEI)).fillna(0.0).clip(0, 1)

        # uptime ~ participation rate in attestations
        denom = df["attestations_total"].replace(0, np.nan)
        uptime = 1.0 - (df["att_missed_total"] / denom)
        uptime = uptime.fillna(1.0).clip(0, 1)
        df["uptime"] = uptime

        df["missed_att"] = df["att_missed_total"].astype(int)
        df["missed_prop"] = df["prop_missed_total"].astype(int)

        # Trim to the columns we actually use downstream
        keep = ["validator_index","slashed","stake","uptime","missed_att","missed_prop"]
    df["validator_index"] = pd.to_numeric(df["validator_index"], errors="coerce").astype("Int64")

    aligned = df[keep].dropna(subset=["validator_index"]).copy()
    aligned["validator_index"] = aligned["validator_index"].astype(int)

    return aligned

    def get(self) -> pd.DataFrame:
        if self.data is None:
            return self.load()
        return self.data
