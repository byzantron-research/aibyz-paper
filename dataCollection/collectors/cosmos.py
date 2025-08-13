from typing import List, Optional, Dict, Any
from pathlib import Path
from tqdm import tqdm
from common.http import get_json
from common.storage import write_rows, part_path, write_provenance
from common.provenance import Provenance
from common.schemas import Block, Validator, Penalty
from common.utils import to_unix

class CosmosCollector:
    def __init__(self, cfg: dict):
        self.chain_id = "cosmos"
        self.network = cfg.get("network","cosmoshub-4")
        self.base = cfg.get("rest","http://localhost:1317")
        self.format = cfg.get("format","parquet")
        self.root = Path(cfg.get("root","."))

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None):
        return get_json(f"{self.base}{path}", params=params)

    def _latest(self) -> int:
        latest = self._get("/cosmos/base/tendermint/v1beta1/blocks/latest")
        return int(latest["block"]["header"]["height"])

    def collect(self, datasets: List[str], start: Optional[int], end: Optional[int], limit: Optional[int], ingest_date: str):
        if start is None and end is None:
            tip = self._latest()
            end = tip
            lookback = limit or 2000
            start = max(1, end - lookback + 1)
        elif end is None:
            tip = self._latest()
            end = min(tip, start + (limit or 1000) - 1)

        if "blocks" in datasets:
            self._blocks(start, end, ingest_date)
        if "validators" in datasets:
            self._validators(ingest_date)
        if "slashings" in datasets:
            self._penalties(start, end, ingest_date)

    def _blocks(self, start: int, end: int, date: str):
        rows = []
        for h in tqdm(range(start, end+1), desc="cosmos blocks"):
            try:
                b = self._get(f"/cosmos/base/tendermint/v1beta1/blocks/{h}")
                hdr = b["block"]["header"]
                rows.append(Block(
                    chain_id=self.chain_id, network=self.network,
                    height_or_slot=int(hdr["height"]),
                    block_hash=b.get("block_id",{}).get("hash"),
                    proposer_address=hdr.get("proposer_address"),
                    timestamp_utc=int(to_unix(hdr["time"]))
                ).model_dump())
            except Exception:
                continue
        out = part_path(self.root, "raw", "blocks", self.chain_id, self.network, date)
        write_rows(rows, out, self.format)
        write_provenance(out, Provenance(self.base, None, "cosmos.blocks", self.chain_id, self.network, "blocks", len(rows)).to_dict())

    def _validators(self, date: str):
        rows = []
        v = self._get("/cosmos/staking/v1beta1/validators", params={"status":"BOND_STATUS_BONDED","pagination.limit":"1000"})
        from time import time
        snap = int(time())
        for val in v.get("validators", []):
            rows.append(Validator(
                chain_id=self.chain_id, network=self.network, snapshot_ts=snap,
                validator_id=val.get("operator_address",""),
                status=val.get("status"),
                commission=float(val.get("commission",{}).get("commission_rates",{}).get("rate", 0.0))
            ).model_dump())
        out = part_path(self.root, "raw", "validators", self.chain_id, self.network, date)
        write_rows(rows, out, self.format)
        write_provenance(out, Provenance(self.base, None, "cosmos.validators", self.chain_id, self.network, "validators", len(rows)).to_dict())

    def _penalties(self, start: int, end: int, date: str):
        rows = []
        import json
        for h in tqdm(range(start, end+1), desc="cosmos penalties"):
            try:
                txs = self._get("/cosmos/tx/v1beta1/txs", params={"events": f"tx.height={h}", "pagination.limit": "200"})
                for tx in txs.get("tx_responses", []):
                    for log in tx.get("logs", []):
                        for ev in log.get("events", []):
                            t = ev.get("type")
                            if t in ("slash", "unjail"):
                                rows.append(dict(
                                    chain_id=self.chain_id, network=self.network,
                                    height_or_slot=h, penalty_type=t, meta_json=json.dumps(ev)
                                ))
            except Exception:
                continue
        out = part_path(self.root, "raw", "penalties", self.chain_id, self.network, date)
        write_rows(rows, out, self.format)
        write_provenance(out, Provenance(self.base, None, "cosmos.penalties", self.chain_id, self.network, "penalties", len(rows)).to_dict())
