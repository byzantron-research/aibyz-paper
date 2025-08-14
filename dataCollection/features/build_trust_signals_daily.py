from pathlib import Path
import pandas as pd
import numpy as np
from common.storage import part_path, write_rows

def _z(x):
    if len(x) == 0: return x
    mu, sd = np.nanmean(x), np.nanstd(x)
    if sd == 0 or np.isnan(sd): return np.zeros_like(x)
    return (x - mu) / sd

def build_trust_signals_daily(cfg: dict, date: str):
    root = Path(cfg.get("root","."))
    chain = cfg["chain_id"]
    net = cfg["network"]
    fmt = cfg.get("format","parquet")

    stats_p = part_path(root, "features", "validator_stats_daily", chain, net, date)
    files = list(stats_p.glob("*.parquet")) + list(stats_p.glob("*.csv"))
    if not files: return
    df = pd.read_parquet(files[0]) if files[0].suffix==".parquet" else pd.read_csv(files[0])

    # Simple composite: z(attestation_rate) + 0.5*z(proposed_blocks)
    df["z_att"] = _z(df["attestation_rate"].astype(float))
    df["z_prop"] = _z(df["proposed_blocks"].astype(float))
    df["trust_score_v1"] = df["z_att"] + 0.5*df["z_prop"]

    out_rows = df[["chain_id","network","date","validator_id","trust_score_v1"]].to_dict(orient="records")
    out_dir = part_path(root, "features", "trust_signals_daily", chain, net, date)
    write_rows(out_rows, out_dir, fmt)
