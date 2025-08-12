from datetime import datetime, timezone

def to_unix(ts_iso: str) -> int:
    from dateutil import parser as dt
    return int(dt.parse(ts_iso).replace(tzinfo=None).astimezone(timezone.utc).timestamp())

def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
