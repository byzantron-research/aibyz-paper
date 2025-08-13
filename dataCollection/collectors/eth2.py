from typing import List, Optional, Dict, Any
from pathlib import Path
from tqdm import tqdm

from common.http import get_json
from common.storage import write_rows, part_path, write_provenance
from common.provenance import Provenance
from common.schemas import Block, Validator, Attestation, Penalty

class Eth2Collector:
    def __init__(self, cfg: dict):
        self.chain_id = "eth2"
        self.network = cfg.get("network","mainnet")
        self.base = cfg.get("beacon","http://localhost:5052")
        self.format = cfg.get("format","parquet")
        self.root = Path(cfg.get("root","."))

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None):
        data = get_json(f"{self.base}{path}", params=params)
        return data.get("data", data)

    def _latest_slot(self) -> int:
        head = self._get("/eth/v1/beacon/headers/head")
        return int(head["header"]["message"]["slot"])

    def collect(self, datasets: List[str], start: Optional[int], end: Optional[int], limit: Optional[int], ingest_date: str):
        # Defaults
        if start is None and end is None:
            latest = self._latest_slot()
            end = latest
            lookback = limit or 512
            start = max(0, latest - lookback + 1)
        elif end is None:
            latest = self._latest_slot()
            end = min(latest, start + (limit or 256) - 1)

        if "blocks" in datasets:
            self._blocks(start, end, ingest_date)
        if "validators" in datasets:
            self._validators(ingest_date)
        if "attestations" in datasets:
            self._attestations(start, end, ingest_date)
        if "slashings" in datasets:
            self._slashings(start, end, ingest_date)

    def _blocks(self, start: int, end: int, date: str):
        rows = []
        for slot in tqdm(range(start, end+1), desc="eth2 blocks"):
            try:
                b = self._get(f"/eth/v2/beacon/blocks/{slot}")
                msg = b["message"]
                rows.append(Block(
                    chain_id=self.chain_id,
                    network=self.network,
                    height_or_slot=slot,
                    epoch=slot//32,
                    block_hash=b.get("root"),
                    parent_hash=(msg["body"].get("execution_payload") or {}).get("parent_hash"),
                    proposer_index=int(msg["proposer_index"]),
                    timestamp_utc=int((msg["body"].get("execution_payload") or {}).get("timestamp") or 0) or None
                ).model_dump())
            except Exception:
                continue
        out_dir = part_path(self.root, "raw", "blocks", self.chain_id, self.network, date)
        write_rows(rows, out_dir, self.format)
        write_provenance(out_dir, Provenance(self.base, None, "eth2.blocks", self.chain_id, self.network, "blocks", len(rows)).to_dict())

    def _validators(self, date: str):
        data = self._get("/eth/v1/beacon/states/head/validators")
        rows = []
        from time import time
        snap = int(time())
        for v in data:
            info = v["validator"]
            rows.append(Validator(
                chain_id=self.chain_id, network=self.network, snapshot_ts=snap,
                validator_id=str(v["index"]),
                status=v.get("status"),
                balance=int(info.get("balance",0)),
                effective_balance=int(info.get("effective_balance",0)),
                slashed=bool(info.get("slashed", False))
            ).model_dump())
        out_dir = part_path(self.root, "raw", "validators", self.chain_id, self.network, date)
        write_rows(rows, out_dir, self.format)
        write_provenance(out_dir, Provenance(self.base, None, "eth2.validators", self.chain_id, self.network, "validators", len(rows)).to_dict())

    def _attestations(self, start: int, end: int, date: str):
        rows = []
        for slot in tqdm(range(start, end+1), desc="eth2 attestations"):
            try:
                b = self._get(f"/eth/v2/beacon/blocks/{slot}")
                msg = b["message"]
                for att in msg["body"].get("attestations", []):
                    d = att["data"]
                    rows.append(Attestation(
                        chain_id=self.chain_id, network=self.network,
                        height_or_slot=slot, epoch=slot//32,
                        committee_index=int(d.get("index",0)),
                        head_block_root=d.get("beacon_block_root"),
                        source_epoch=int(d["source"]["epoch"]),
                        target_epoch=int(d["target"]["epoch"]),
                    ).model_dump())
            except Exception:
                continue
        out_dir = part_path(self.root, "raw", "attestations", self.chain_id, self.network, date)
        write_rows(rows, out_dir, self.format)
        write_provenance(out_dir, Provenance(self.base, None, "eth2.attestations", self.chain_id, self.network, "attestations", len(rows)).to_dict())

    def _slashings(self, start: int, end: int, date: str):
        rows = []
        import json as _json
        for slot in tqdm(range(start, end+1), desc="eth2 slashings"):
            try:
                b = self._get(f"/eth/v2/beacon/blocks/{slot}")
                msg = b["message"]
                for s in msg["body"].get("proposer_slashings", []):
                    rows.append(Penalty(chain_id=self.chain_id, network=self.network,
                        height_or_slot=slot, penalty_type="proposer_slashing",
                        meta_json=_json.dumps(s)).model_dump())
                for s in msg["body"].get("attester_slashings", []):
                    rows.append(Penalty(chain_id=self.chain_id, network=self.network,
                        height_or_slot=slot, penalty_type="attester_slashing",
                        meta_json=_json.dumps(s)).model_dump())
            except Exception:
                continue
        out_dir = part_path(self.root, "raw", "penalties", self.chain_id, self.network, date)
        write_rows(rows, out_dir, self.format)
        write_provenance(out_dir, Provenance(self.base, None, "eth2.penalties", self.chain_id, self.network, "penalties", len(rows)).to_dict())
