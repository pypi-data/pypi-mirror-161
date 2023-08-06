from collections import deque
from datetime import datetime
import asyncio
from typing import Dict, List

import zmq

from ..logger import Logger
from ..timer import Timer
from ..zmq.socket import AsyncContext
from ..clients import get_historic_prices_factory
from .signals import Stop
from ..clients.commons import symbol_to_tickerId

from ..models import (
    increment,
)


async def wait_for_get_historic_price(api, symbol, batch_size, end_at, logger):
    while True:
        try:
            _, _, _, it = await api(symbol=symbol, count=batch_size, time=end_at)
            break
        except Exception:
            logger.error(f"exception getting historic price: {e}")
            end_at >>= 1
    return it


async def push_future_quote_price(
    symbol: str,
    logger: Logger,
    timer: Timer,
    stop_event: asyncio.Event,
    broker_socks,
    batch_size: int = 10,
):
    logger.debug("in push future quote price")
    # raise Exception("testing")
    start_at = timer.now() << 0
    end_at = start_at >> batch_size
    api = get_historic_prices_factory("backtest")

    data = deque()

    while not stop_event.is_set():
        now = timer.now()
        end_at = now >> batch_size

        if not data or data[-1].time <= now:
            it = await wait_for_get_historic_price(
                api, symbol, batch_size, end_at, logger
            )
            data.extend(reversed(list(it)))

        while data:
            if data[0].time < (now << 0):
                data.popleft()
            else:
                break

        if len(data) < 2:
            logger.exception(f"insufficient data, len of data: {len(data)}")
            await timer.sleep(1)
            continue

        # linear interpolation
        duration = data[1].time.timestamp() - data[0].time.timestamp()
        if duration == 0:
            price = data[1].close
        else:
            price = data[0].close + (data[1].close - data[0].close) * (
                now.timestamp() - data[0].time.timestamp()
            ) / (data[1].time.timestamp() - data[0].time.timestamp())
        # NOTE following is for debug:
        # price = data[0].close
        # logger.debug(
        #     f"now: {now}, now-ls: {now << 0} d[0].time: {data[0].time}, "
        #     f"data[0].price: {data[0].close}, "
        #     f"data[1].price: {data[1].close}, price: {price}"
        # )

        payload = {
            "deal": {
                "tradeDate": now.isoformat(),
                "price": price,
            },
            "tickerId": symbol_to_tickerId(symbol),
        }

        for broker_sock in broker_socks:
            await broker_sock.send(payload)
        await timer.sleep(0.5)


def get_next_trading_minute(t: str):
    t = datetime.fromisoformat(t)
    return increment(t, 0)


def BacktestQuotePriceFeeder(
    id: str,
    in_ctrl_addr: str,
    out_ctrl_addr: str,
    start_at: str,
    symbols: List[str],
    timer_args: Dict,
    broker_addr: List[str],
    log_level: str = "DEBUG",
    **kwargs,
):

    exc = None
    zmqctx = AsyncContext()
    timer = Timer(**timer_args)
    logger = Logger(id, timer=timer, level=log_level)
    stop_event = asyncio.Event()
    in_ctrl_sock = zmqctx.socket(zmq.PULL)
    in_ctrl_sock.bind(in_ctrl_addr)
    out_ctrl_sock = zmqctx.socket(zmq.PUSH)
    out_ctrl_sock.connect(out_ctrl_addr)

    broker_socks = []
    for addr in broker_addr:
        broker_sock = zmqctx.socket(zmq.PUSH)
        broker_sock.connect(addr)
        broker_socks.append(broker_sock)

    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    start_at = get_next_trading_minute(start_at)

    async def in_ctrl_listen():
        nonlocal stop_event, exc
        while True:
            msg = await in_ctrl_sock.recv()
            if isinstance(msg, (Exception, Stop)):
                stop_event.set()
                break

    tasks = []
    tasks.append(loop.create_task(in_ctrl_listen()))

    for symbol in symbols:
        tasks.append(
            loop.create_task(
                push_future_quote_price(symbol, logger, timer, stop_event, broker_socks)
            )
        )

    done, pending = loop.run_until_complete(
        asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    )
    timer.close()

    for task in done | pending:
        try:
            exc = task.exception()
        except asyncio.exceptions.InvalidStateError:
            pass

    if exc:
        logger.debug(f"raise exception {exc} from immortal")
        raise exc

    for sock in [in_ctrl_sock, out_ctrl_sock]:
        sock.setsockopt(zmq.LINGER, 0)
        sock.close()
    zmqctx.term()
