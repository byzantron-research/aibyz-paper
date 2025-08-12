from typing import Optional, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class HTTPError(Exception): ...

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10),
       retry=retry_if_exception_type((requests.RequestException,)))
def get_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = 30):
    r = requests.get(url, params=params, timeout=timeout)
    if r.status_code != 200:
        raise HTTPError(f"GET {url} -> {r.status_code} {r.text[:200]}")
    return r.json()
