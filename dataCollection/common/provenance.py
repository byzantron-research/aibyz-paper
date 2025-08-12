from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class Provenance:
    source: str
    api_version: Optional[str]
    collector: str
    chain_id: str
    network: str
    dataset: str
    rows: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
