from typing import List, Optional
from pathlib import Path
from tqdm import tqdm
from substrateinterface import SubstrateInterface
from common.storage import write_rows, part_path, write_provenance
from common.provenance import Provenance
from common.schemas import Block, Validator

class PolkadotCollector:
    def __init__(self, cfg: dict):
        self.chain_id = "polkadot"
        self.network = cfg.get("network","mainnet")
        self.ws = cfg.get("ws","wss://rpc.polkadot.io")
        self.format = cfg.get("format","parquet")
        self.root = Path(cfg.get("root","."))

        self.substrate = SubstrateInterface(url=self.ws)

    def _latest(self) -> int:
        head = self.substrate.get_chain_head()
        header = self.substrate.get_block_header(head)
        return int(header["number"])

    def collect(self, datasets: List[str], start: Optional[int], end: Optional[int], limit: Optional[int], ingest_date: str):
        if start is None and end is None:
            tip = self._latest()
            end = tip
            start = max(1, end - (limit or 1000) + 1)
        elif end is None:
            tip = self._latest()
            end = min(tip, start + (limit or 500) - 1)

        if "blocks" in datasets:
            self._blocks(start, end, ingest_date)
        if "validators" in datasets:
            self._validators(ingest_date)

    def _blocks(self, start: int, end: int, date: str):
        rows = []
        for h in tqdm(range(start, end+1), desc="polkadot blocks"):
            try:
                bh = self.substrate.get_block_hash(block_id=h)
                hdr = self.substrate.get_block_header(block_hash=bh)
                rows.append(Block(
                    chain_id=self.chain_id, network=self.network,
                    height_or_slot=h, block_hash=str(bh),
                    parent_hash=str(hdr["parentHash"])
                ).model_dump())
            except Exception:
                continue
        out = part_path(self.root, "raw", "blocks", self.chain_id, self.network, date)
        write_rows(rows, out, self.format)
        write_provenance(out, Provenance(self.ws, None, "polkadot.blocks", self.chain_id, self.network, "blocks", len(rows)).to_dict())

    def _validators(self, date: str):
        rows = []
        res = self.substrate.query(module='Session', storage_function='Validators')
        for acc in res.value or []:
            rows.append(Validator(chain_id=self.chain_id, network=self.network, snapshot_ts=0, validator_id=acc).model_dump())
        out = part_path(self.root, "raw", "validators", self.chain_id, self.network, date)
        write_rows(rows, out, self.format)
        write_provenance(out, Provenance(self.ws, None, "polkadot.validators", self.chain_id, self.network, "validators", len(rows)).to_dict())
