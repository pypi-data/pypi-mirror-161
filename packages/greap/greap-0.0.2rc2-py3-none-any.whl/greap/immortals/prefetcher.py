from functools import partial
from collections import deque
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Callable
import asyncio
import zmq
import sqlalchemy
from sqlmodel import Session, SQLModel, update
from sqlalchemy.sql.expression import bindparam
from rich.progress import track


from ..db import create_engine
from ..logger import Logger
from ..zmq.socket import AsyncContext
from .signals import (
    Stop,
    FetchLockAcquire,
    FetchLockRelease,
    FetchLockAcquireStatus,
    FetchLockReleaseStatus,
    PrefetchCompleted,
)
from ..timer import Timer
from ..clients import get_historic_prices_factory
from ..profiler import timeit

from ..models import (
    increment,
    decrement,
    MAX_COUNT,
    UNCERTAIN_WINDOW,
    Price,
    MissingPrice,
    Symbol,
)


def merge(l1: deque, l2: deque):
    res = []
    while l1 and l2:
        if l1[0] >= l2[0]:
            res.append(l2.popleft())
        else:
            res.append(l1.popleft())
    res.extend(l1)
    res.extend(l2)
    return res


def get_request_intervals(
    sess, symbol_schema, symbol_name, start_at, end_at, metas, fetch_all
):
    if not fetch_all and metas["start_at"] <= start_at:
        start_at = metas["end_at"]

    if start_at > end_at:
        return {}

    stored_time = deque(
        q[0]
        for q in sess.query(symbol_schema.time).where(symbol_schema.time >= start_at)
    )

    miss_time = deque(
        q[0]
        for q in sess.query(MissingPrice.time)
        .where(MissingPrice.symbol == symbol_name)
        .where(MissingPrice.time >= start_at)
        .order_by(MissingPrice.time)
    )

    stored_time = merge(stored_time, miss_time)

    results = defaultdict(int)
    time = start_at
    i = 0
    while time < end_at:
        if len(stored_time) == 0:
            results[start_at] += 1
            time = increment(time, 1)
        elif i == len(stored_time) or stored_time[i] > time:
            results[increment(stored_time[i - 1]) if i > 0 else start_at] += 1
            time = increment(time, 1)
        elif stored_time[i] < time:
            # TODO: this block should not really happen if MissingPrice is
            # inserted correctly. Anyhow, if invalid MissingPrice is inserted,
            # we increment i until stored_time[i] == time
            i += 1
        else:
            i += 1
            time = increment(time, 1)

    # second pass to split request with count > MAX_COUNT
    new_results = {}
    for t, count in results.items():
        new_time = t
        while count > 0:
            new_count = min(MAX_COUNT, count)
            new_time = increment(new_time, new_count - 1)
            new_results[new_time] = new_count
            new_time = increment(new_time)
            count -= new_count

    return new_results


def get_next_trading_minute(t: str):
    t = datetime.fromisoformat(t)
    return increment(t, 0)


async def fetch(
    api: Callable,
    loop: asyncio.events.AbstractEventLoop,
    conn: sqlalchemy.future.engine.Engine,
    schemas: Dict[str, SQLModel],
    start_at: datetime,
    timer: Timer,
    logger: Logger,
    source: str,
    report_progress: bool,
    fetch_all: bool = True,
):
    updated = False
    tasks = []
    now = timer.now()

    with Session(conn) as sess:
        metas = {
            sym.name: {"start_at": sym.start_at, "end_at": sym.end_at}
            for sym in sess.query(Symbol)
        }

    req = {}
    # get request for stock prices given start_at and using MissingPrice table
    with Session(conn) as sess:
        for symbol, schema in schemas.items():
            req[symbol] = get_request_intervals(
                sess, schema, symbol, start_at, now, metas[symbol], fetch_all
            )
            logger.debug(req)
            if req[symbol]:
                for k, v in req[symbol].items():
                    logger.debug(
                        "request last {count} price(s) for {symbol} ending at {d}".format(  # noqa: E501
                            symbol=symbol, d=str(k), count=v
                        )
                    )

    # download price data
    for symbol, req_data in req.items():
        for time, count in req_data.items():
            t = loop.create_task(
                api(
                    symbol=symbol,
                    count=count,
                    time=time,
                )
            )
            tasks.append(t)

    # update stock prices and missing prices
    wrap = (
        partial(track, description="Downloading prices...", total=len(tasks))
        if report_progress
        else lambda x: x
    )
    with Session(conn) as sess:
        for task in wrap(asyncio.as_completed(tasks)):
            try:
                symbol, count, end, it = await task
            except Exception as e:
                logger.debug(f"{type(e)}: {str(e)}, cannot get prices")
                continue

            missing = {decrement(end, m) for m in range(count)}
            price_items = []
            for data in it:
                missing.discard(data.time)
                price_items.append(
                    schemas[symbol](
                        time=data.time,
                        open=data.open,
                        high=data.high,
                        low=data.low,
                        close=data.close,
                        volume=data.volume,
                        vwap=data.vwap,
                    )
                )

            updated = updated or price_items is not None
            for item in price_items:
                sess.merge(item)

            for time in missing:
                if (
                    now - time > timedelta(minutes=UNCERTAIN_WINDOW)
                    and increment(time, 0) == time
                ):
                    sess.merge(MissingPrice(time=time, symbol=symbol))

        sess.commit()

    # update price metas
    with Session(conn) as sess:
        set_symbol_metas_stmt = (
            update(Symbol)
            .values(end_at=bindparam("end_at"))
            .values(start_at=bindparam("start_at"))
        )
        new_metas = [
            {
                "end_at": max(old["end_at"], now << UNCERTAIN_WINDOW),
                "start_at": min(old["start_at"], start_at),
            }
            for old in metas.values()
        ]
        if new_metas:
            sess.execute(set_symbol_metas_stmt, new_metas)
            sess.commit()

    if updated:
        return True

    with Session(conn) as sess:
        for symbol, schema in schemas.items():
            t = sess.query(schema.time).where(schema.time >= (now << 0))
            if t:
                return True
        return False


def Prefetcher(
    id: str,
    in_ctrl_addr: str,
    out_ctrl_addr: str,
    database_addr: str,
    interval: float,
    start_at: str,
    symbols: List[str],
    timer_args: Dict,
    source: str,
    report_progress: bool,
    log_level: str = "DEBUG",
    **kwargs,
):
    print("source", source)
    exc = None
    zmqctx = AsyncContext()
    timer = Timer(**timer_args)
    logger = Logger(id, timer=timer, level=log_level)
    stop_event = asyncio.Event()
    in_ctrl_sock = zmqctx.socket(zmq.PULL)
    in_ctrl_sock.bind(in_ctrl_addr)
    out_ctrl_sock = zmqctx.socket(zmq.PUSH)
    out_ctrl_sock.connect(out_ctrl_addr)

    loop = asyncio.get_event_loop()

    if log_level == "DEBUG":
        loop.set_debug(True)

    conn = create_engine(database_addr)
    acquire = asyncio.Event()
    release = asyncio.Event()
    start_at = get_next_trading_minute(start_at)

    schemas = {}
    for symbol in symbols:
        cls = type(symbol, (Price,), {}, table=True)
        schemas[symbol] = cls

    try:
        SQLModel.metadata.create_all(conn)
    except sqlalchemy.exc.OperationalError:
        pass

    with Session(conn) as sess:
        for symbol in symbols:
            sess.merge(Symbol(name=symbol, start_at=start_at, end_at=start_at))
        sess.commit()

    try:
        SQLModel.metadata.create_all(conn)
    except sqlalchemy.exc.OperationalError:
        pass

    api = get_historic_prices_factory(source)

    async def fetch_task():
        with timeit("prefetch", logger.debug):
            updated = await fetch(
                api,
                loop,
                conn,
                schemas,
                start_at,
                timer,
                logger,
                source,
                report_progress,
            )
        await out_ctrl_sock.send(PrefetchCompleted())
        logger.debug("PrefetchCompleted sent")
        nonlocal stop_event
        while not stop_event.is_set():
            # TODO: introduce better locking with fencing as per:
            # https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
            await out_ctrl_sock.send(PrefetchCompleted())
            await out_ctrl_sock.send(FetchLockAcquire())
            # await acquire.wait()
            # acquire.clear()
            with timeit("fetch", logger.debug):
                updated = await fetch(
                    api,
                    loop,
                    conn,
                    schemas,
                    start_at,
                    timer,
                    logger,
                    source,
                    report_progress,
                    False,
                )
            logger.debug(f"fetch updated: {updated}")
            await out_ctrl_sock.send(FetchLockRelease(updated=updated))
            # await release.wait()
            # release.clear()
            slept = await timer.maintain_interval(interval)
            if not slept:
                logger.error(
                    "proc did not sleep during maintain interval; "
                    "slow down timer to avoid throttling"
                )

    async def in_ctrl_listen():
        nonlocal stop_event
        while True:
            msg = await in_ctrl_sock.recv()
            if isinstance(msg, FetchLockAcquireStatus) and msg.ok:
                acquire.set()
            if isinstance(msg, FetchLockReleaseStatus) and msg.ok:
                release.set()
            if isinstance(msg, Stop):
                stop_event.set()
                break

    tasks = []
    tasks.append(loop.create_task(fetch_task()))
    tasks.append(loop.create_task(in_ctrl_listen()))
    done, pending = loop.run_until_complete(
        asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    )
    timer.close()
    for task in done:
        try:
            exc = task.exception()
        except Exception:
            pass
    if exc:
        raise exc
