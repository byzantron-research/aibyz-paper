from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import json
from datetime import datetime, timezone

def ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

def part_path(root: Path, layer: str, table: str, chain_id: str, network: str, date: str) -> Path:
    return root / layer / table / f"chain_id={chain_id}" / f"network={network}" / f"date={date}"

def write_rows(rows: List[Dict[str, Any]], out_dir: Path, fmt: str = "parquet", filename: str = "part-000"):
    ensure_dir(out_dir)
    if not rows: return
    df = pd.DataFrame(rows)
    if fmt == "csv":
        df.to_csv(out_dir / f"{filename}.csv", index=False)
    else:
        df.to_parquet(out_dir / f"{filename}.parquet", index=False)

def write_provenance(out_dir: Path, info: Dict[str, Any]):
    ensure_dir(out_dir)
    info["written_at_utc"] = int(datetime.now(timezone.utc).timestamp())
    with open(out_dir / "provenance.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
