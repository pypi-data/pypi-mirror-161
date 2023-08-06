from typing import Callable
import asyncio
import asyncio_mqtt
from datetime import datetime

from asyncer import asyncify
from webull import webull


from .utils import PriceTuple, tz
from .commons import symbol_to_tickerId, parse_price


wb = webull()


async def quote_price_subscribe(
    queue: asyncio.Queue, is_alive: Callable, broker_addr: str, symbols: list = []
):
    global quote_prices

    broker_addr = broker_addr or wb._did

    client = asyncio_mqtt.Client(broker_addr, username="test", password="test")

    while is_alive():
        try:
            await client.connect(timeout=1)
        except asyncio_mqtt.error.MqttError:
            pass
        else:
            break

    if not is_alive():
        return

    tId = [symbol_to_tickerId(symbol) for symbol in symbols]
    subscribee = "{" + f'"tickerIds":{tId},"type":"105"' + "}"

    async with client.unfiltered_messages() as messages:
        await client.subscribe(subscribee)
        async for message in messages:
            symbol, time, price = parse_price(message)
            quote_prices[symbol].insert(time, price)
            await queue.put((symbol, time, price))
            if not is_alive():
                break

    await client.force_disconnect()


def _gen(it):
    for ts, row in it.iterrows():
        ts = ts.replace(tzinfo=None)
        yield PriceTuple(
            time=ts,
            open=row[0],
            high=row[1],
            low=row[2],
            close=row[3],
            volume=row[4],
            vwap=row[5],
        )


async def get_historic_prices(symbol: str, count: int, time: datetime):
    it = await asyncify(wb.get_bars)(
        stock=symbol, count=count, timeStamp=int(tz.localize(time).timestamp())
    )
    return symbol, count, time, _gen(it)


def get_quote_price(symbol: str, type: str = "close"):
    res = wb.get_quote(symbol)
    return (
        datetime.fromisoformat(res["tradeTime"][:-5])
        # .replace(tzinfo=nytz)
    ), float(res[type])
