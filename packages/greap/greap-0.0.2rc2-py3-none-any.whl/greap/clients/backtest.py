from typing import Callable, Union
import asyncio
import zmq
import uuid
from typing import Optional
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import column, table, select, literal_column

from .utils import PriceTuple
from .commons import quote_prices, parse_price
from ..zmq.socket import AsyncContext


orders = {}


def _gen(it, count: int, time: datetime):
    for data in it:
        t = datetime.fromisoformat(data.time).replace(tzinfo=None)
        yield PriceTuple(
            time=t,
            open=data.open,
            high=data.high,
            low=data.low,
            close=data.close,
            volume=data.volume,
            vwap=data.vwap,
        )


async def get_historic_prices(symbol: str, count: int, time: datetime):
    dbpath = Path(os.environ["BACKTEST_DATA_PATH"])
    conn = create_async_engine(f"sqlite+aiosqlite:///{dbpath}")
    async with AsyncSession(conn) as sess:
        it = await sess.execute(
            select(literal_column("*"))
            .select_from(table(symbol))
            .where(column("time") <= time)
            .order_by(column("time").desc())
            .limit(count)
        )
        return symbol, count, time, _gen(it, count, time)


def get_quote_price(symbol: str, type: str = "close"):
    print("symbol: ", symbol, quote_prices[symbol])
    times, prices = quote_prices[symbol][-1:]
    price = None if not prices else prices[0]
    return (times and times[0]) or datetime.max, price


async def create_order(
    symbol: str,
    quantity: str,
    price: float,
    stop_price: float,
    submit_at: Optional[datetime] = None,
    close: bool = False,
    type="limit",
):
    id_ = str(uuid.uuid1())
    global orders
    d = orders[id_] = {
        "created_at": str(submit_at),
        "filled_at": str(submit_at),
        "filled_avg_price": price,
        "filled_qty": quantity,
        "id": id_,
        "order_type": "stop_limit",
        "qty": quantity,
        "side": "sell" if close else "buy",
        "status": "filled",
        "stop_price": stop_price,
        "submitted_at": str(submit_at),
        "symbol": symbol,
        "time_in_force": "day",
        "type": "stop_limit",
        "updated_at": str(submit_at),
    }
    return d["id"], datetime.fromisoformat(d["created_at"]), close


def get_order(order_id):
    global orders
    return orders[order_id]


async def quote_price_subscribe(
    queue: asyncio.Queue, is_alive: Callable, broker_addr: Union[str, None]
):

    if broker_addr is None:
        # this is for ease of testing
        while is_alive():
            await asyncio.sleep(1)
        return

    ctx = AsyncContext()
    broker_sock = ctx.socket(zmq.PULL)
    broker_sock.bind(broker_addr)

    while is_alive():
        message = await broker_sock.recv()
        symbol, time, price = parse_price(message)
        quote_prices[symbol].insert(time, price)
        await queue.put((symbol, time, price))

    ctx.term()
    raise Exception("done")
