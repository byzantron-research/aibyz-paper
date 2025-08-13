from pathlib import Path
import pandas as pd
from common.storage import ensure_dir, part_path, write_rows
from common.utils import today_str

class Curator:
    """
    Minimal normalizer:
      - block_core
      - validator_core
      - attestation_core
      - penalty_core
    """
    def __init__(self, cfg: dict):
        self.chain_id = cfg["chain_id"]
        self.network = cfg["network"]
        self.root = Path(cfg.get("root","."))
        self.format = cfg.get("format","parquet")

    def _read_any(self, layer: str, table: str, date: str) -> pd.DataFrame:
        base = part_path(self.root, layer, table, self.chain_id, self.network, date)
        if not base.exists(): return pd.DataFrame()
        files = list(base.glob("*.parquet")) + list(base.glob("*.csv"))
        if not files: return pd.DataFrame()
        dfs = []
        for f in files:
            if f.suffix == ".csv":
                dfs.append(pd.read_csv(f))
            else:
                dfs.append(pd.read_parquet(f))
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def curate(self, ingest_date: str):
        date = ingest_date or today_str()

        # blocks -> block_core
        raw_blocks = self._read_any("raw", "blocks", date)
        if not raw_blocks.empty:
            out = part_path(self.root, "curated", "block_core", self.chain_id, self.network, date)
            # rename/ensure columns
            cols = ["chain_id","network","height_or_slot","epoch","block_hash","parent_hash","proposer_index","proposer_address","timestamp_utc"]
            for c in cols:
                if c not in raw_blocks.columns:
                    raw_blocks[c] = None
            write_rows(raw_blocks[cols].drop_duplicates(subset=["chain_id","network","height_or_slot"]), out, self.format)

        # validators -> validator_core
        raw_vals = self._read_any("raw", "validators", date)
        if not raw_vals.empty:
            out = part_path(self.root, "curated", "validator_core", self.chain_id, self.network, date)
            cols = ["chain_id","network","snapshot_ts","validator_id","status","balance","effective_balance","commission","slashed"]
            for c in cols:
                if c not in raw_vals.columns:
                    raw_vals[c] = None
            # PK uniqueness
            raw_vals = raw_vals.drop_duplicates(subset=["chain_id","network","snapshot_ts","validator_id"])
            write_rows(raw_vals[cols], out, self.format)

        # attestations -> attestation_core
        raw_atts = self._read_any("raw", "attestations", date)
        if not raw_atts.empty:
            out = part_path(self.root, "curated", "attestation_core", self.chain_id, self.network, date)
            cols = ["chain_id","network","height_or_slot","epoch","committee_index","head_block_root","source_epoch","target_epoch"]
            for c in cols:
                if c not in raw_atts.columns: raw_atts[c] = None
            raw_atts = raw_atts.drop_duplicates(subset=["chain_id","network","height_or_slot","committee_index","head_block_root"])
            write_rows(raw_atts[cols], out, self.format)

        # penalties -> penalty_core
        raw_pen = self._read_any("raw", "penalties", date)
        if not raw_pen.empty:
            out = part_path(self.root, "curated", "penalty_core", self.chain_id, self.network, date)
            cols = ["chain_id","network","height_or_slot","validator_id","penalty_type","value","meta_json"]
            for c in cols:
                if c not in raw_pen.columns: raw_pen[c] = None
            write_rows(raw_pen[cols].drop_duplicates(), out, self.format)
