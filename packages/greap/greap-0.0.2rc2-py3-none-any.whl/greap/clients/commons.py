from datetime import datetime
from functools import lru_cache
from collections import defaultdict
from .utils import Buffer


quote_prices = defaultdict(lambda: Buffer(100))


def parse_price(info):
    symbol = tickerId_to_symbol(info["tickerId"])
    time = datetime.fromisoformat(info["deal"]["tradeDate"])
    price = info["deal"]["price"]
    return symbol, time, price


@lru_cache
def tickerId_to_symbol(tickerId):
    from webull import webull

    wb = webull()
    return wb.get_quote(tId=tickerId)["symbol"]


@lru_cache
def symbol_to_tickerId(symbol):
    from webull import webull

    wb = webull()
    return wb.get_ticker(symbol)
