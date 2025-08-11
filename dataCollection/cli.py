import argparse
import sys
from pathlib import Path
import yaml

from common.utils import today_str
from collectors.eth2 import Eth2Collector
from collectors.cosmos import CosmosCollector
from collectors.polkadot import PolkadotCollector
from curators.common import Curator
from features.build_validator_stats_daily import build_validator_stats_daily
from features.build_trust_signals_daily import build_trust_signals_daily

def load_cfg(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_collector(chain_id: str, cfg: dict):
    if chain_id == "eth2":
        return Eth2Collector(cfg)
    if chain_id == "cosmos":
        return CosmosCollector(cfg)
    if chain_id == "polkadot":
        return PolkadotCollector(cfg)
    raise ValueError(f"Unsupported chain_id {chain_id}")

def main():
    p = argparse.ArgumentParser("dataCollection")
    sub = p.add_subparsers(dest="cmd", required=True)

    # collect
    c = sub.add_parser("collect", help="Collect RAW data")
    c.add_argument("--config", default="config.yaml")
    c.add_argument("--chain", required=True, choices=["eth2","cosmos","polkadot"])
    c.add_argument("--what", default="blocks,validators,attestations,slashings")
    c.add_argument("--start", type=int)
    c.add_argument("--end", type=int)
    c.add_argument("--limit", type=int)
    c.add_argument("--date", default=today_str())

    # curate
    u = sub.add_parser("curate", help="Normalize RAW -> CURATED")
    u.add_argument("--config", default="config.yaml")
    u.add_argument("--chain", required=True, choices=["eth2","cosmos","polkadot"])
    u.add_argument("--date", default=today_str())

    # features
    f = sub.add_parser("features", help="Build daily features")
    f.add_argument("--config", default="config.yaml")
    f.add_argument("--chain", required=True, choices=["eth2","cosmos","polkadot"])
    f.add_argument("--date", default=today_str())

    args = p.parse_args()
    cfg = load_cfg(args.config)

    # Resolve chain-specific cfg
    chain_cfg = None
    for c in cfg["chains"]:
        if c["chain_id"] == args.chain:
            chain_cfg = c
            break
    if not chain_cfg:
        print(f"Chain {args.chain} not found in config.yaml", file=sys.stderr)
        sys.exit(1)
    chain_cfg = {**chain_cfg, "format": cfg.get("format","parquet"), "root": cfg.get("root",".")}

    if args.cmd == "collect":
        collector = get_collector(args.chain, chain_cfg)
        datasets = [x.strip() for x in args.what.split(",") if x.strip()]
        collector.collect(datasets=datasets, start=args.start, end=args.end, limit=args.limit, ingest_date=args.date)
        return

    if args.cmd == "curate":
        Curator(chain_cfg).curate(ingest_date=args.date)
        return

    if args.cmd == "features":
        build_validator_stats_daily(chain_cfg, date=args.date)
        build_trust_signals_daily(chain_cfg, date=args.date)
        return

if __name__ == "__main__":
    main()
