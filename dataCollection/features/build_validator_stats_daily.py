from pathlib import Path
import pandas as pd
import numpy as np
from common.storage import part_path, write_rows

def build_validator_stats_daily(cfg: dict, date: str):
    root = Path(cfg.get("root","."))
    chain = cfg["chain_id"]
    net = cfg["network"]
    fmt = cfg.get("format","parquet")

    # Inputs
    vals_p = part_path(root, "curated", "validator_core", chain, net, date)
    atts_p = part_path(root, "curated", "attestation_core", chain, net, date)
    blocks_p = part_path(root, "curated", "block_core", chain, net, date)

    def read_any(p: Path):
        if p.exists():
            fs = list(p.glob("*.parquet")) + list(p.glob("*.csv"))
            if not fs: return pd.DataFrame()
            dfs = [pd.read_parquet(f) if f.suffix==".parquet" else pd.read_csv(f) for f in fs]
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

    vals = read_any(vals_p)
    atts = read_any(atts_p)
    blocks = read_any(blocks_p)

    # Minimal heuristic features (will refine later)
    out_rows = []
    if not vals.empty:
        # Counts
        proposed_blocks = 0
        if not blocks.empty and "proposer_index" in blocks.columns and blocks["proposer_index"].notna().any():
            # Only available for eth2
            by_prop = blocks.groupby("proposer_index").size().to_dict()
        else:
            by_prop = {}

        # Attestation stats (eth2 only)
        if not atts.empty:
            total_atts = len(atts)
            att_rate = 1.0  # per-validator normalization not available without validator_index expansion
        else:
            total_atts = 0
            att_rate = np.nan

        for _, v in vals.iterrows():
            out_rows.append(dict(
                chain_id=chain, network=net, date=date, validator_id=str(v["validator_id"]),
                attestation_rate=att_rate,
                avg_inclusion_delay=np.nan,   # needs committee expansion
                missed_attestations=np.nan,   # requires per-validator trace
                proposed_blocks=by_prop.get(int(v["validator_id"]) if str(v["validator_id"]).isdigit() else -1, 0),
                slash_count_30d=np.nan,
                stake_share=np.nan,
                churn_events_30d=np.nan,
                uptime_estimate=np.nan
            ))

    out_dir = part_path(root, "features", "validator_stats_daily", chain, net, date)
    write_rows(out_rows, out_dir, fmt)
