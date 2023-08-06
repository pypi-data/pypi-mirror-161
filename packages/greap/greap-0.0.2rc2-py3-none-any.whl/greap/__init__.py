"""Greap framework, a lightweight library to build queue-based trade systems"""

__version__ = "0.0.1"

from forbiddenfruit import curse
from rich.traceback import install
import os
import uvloop

from greap.types import payload  # noqa: F401
import greap.models  # noqa: F401
from pathlib import Path

import resource

try:
    resource.setrlimit(
        resource.RLIMIT_NOFILE, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
    )
except ValueError:
    pass


install(show_locals=False)
uvloop.install()


def isfloat(self):
    try:
        float(self)
    except ValueError:
        return False
    else:
        return True


def toInt(self):
    return int(float(self))


curse(str, "isfloat", isfloat)
curse(str, "toInt", toInt)

CACHE_DIR = Path.home() / ".greap"
CACHE_DIR.mkdir(exist_ok=True)

BACKTEST_DATA_PATH = os.environ.setdefault(
    "BACKTEST_DATA_PATH", str(CACHE_DIR / "backtest.db")
)
