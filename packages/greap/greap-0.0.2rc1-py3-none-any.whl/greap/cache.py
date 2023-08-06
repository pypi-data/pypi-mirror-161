from datetime import datetime
from functools import lru_cache


@lru_cache(maxsize=100000)
def timestamp(t: datetime):
    return t.timestamp()
