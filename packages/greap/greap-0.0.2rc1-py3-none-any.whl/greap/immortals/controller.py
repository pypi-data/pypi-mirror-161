from itertools import chain
import asyncio
from typing import Dict, Any
import zmq
from bidict import bidict

from ..logger import Logger
from ..zmq.socket import AsyncContext
from .signals import (
    Stop,
    PrefetchCompleted,
    ReadyToStart,
    StartRequest,
    FetchLockAcquire,
    FetchLockAcquireStatus,
    FetchDataStatus,
    FetchLockRelease,
    FetchLockReleaseStatus,
    Signal,
)
from ..timer import Timer

# TODO move name_is_valid to validator
from ..spawner.lib import name_is_valid


def _init_sockets(in_addrs, out_addrs, ctx):
    in_socks, out_socks = {}, {}

    for id, addr in in_addrs.items():
        in_sock = ctx.socket(zmq.PULL)
        in_sock.bind(addr)
        in_socks[id] = in_sock

    for id, addr in out_addrs.items():
        out_sock = ctx.socket(zmq.PUSH)
        out_sock.connect(addr)
        out_socks[id] = out_sock

    return bidict(in_socks), bidict(out_socks)


def Controller(
    id: str,
    in_addrs: Dict[str, str],
    out_addrs: Dict[str, str],
    timer_args: Dict,
    log_level: str,
    **kwargs,
):
    timer = Timer(**timer_args)
    ctx = AsyncContext()
    poller = zmq.asyncio.Poller()
    print("controller log level", log_level)
    logger = Logger(id, timer, log_level)
    in_socks, out_socks = _init_sockets(in_addrs, out_addrs, ctx)
    for s in in_socks.values():
        poller.register(s, zmq.POLLIN)

    loop = asyncio.get_event_loop()

    if log_level == "DEBUG":
        loop.set_debug(True)

    # fetch_lock = asyncio.Lock()
    lock_owner = None
    version = 0
    ready_to_start_event = asyncio.Event()

    async def handle_stop(id_in, msg: Stop):
        # NOTE: not doing the following because controller should not
        # be the single point of failure
        if False:
            for out_s in out_socks.values():
                await out_s.send(msg)

        for sock in chain(in_socks.values(), out_socks.values()):
            sock.setsockopt(zmq.LINGER, 0)
            sock.close()

        logger.debug("stopping controller...")
        ctx.term()
        logger.debug("context terminated")
        return True

    async def handle_prefetch_completed(id_in: str, msg: PrefetchCompleted):
        ready_to_start_event.set()
        logger.debug("prefetch completed. ready to start")
        return False

    async def _wait_for_ready_to_start_and_respond(id_in: str):
        await ready_to_start_event.wait()
        await out_socks[id_in].send(ReadyToStart())
        return False

    async def handle_start_request(id_in: str, msg: StartRequest):
        if ready_to_start_event.is_set():
            await out_socks[id_in].send(ReadyToStart())
        else:
            asyncio.create_task(_wait_for_ready_to_start_and_respond(id_in))
        return False

    async def handle_fetch_lock_acquire(id_in: str, msg: FetchLockAcquire):
        # await fetch_lock.acquire()
        logger.debug("lock acquired")
        nonlocal lock_owner
        lock_owner = id_in
        await out_socks[id_in].send(FetchLockAcquireStatus(ok=True))
        for id_out, out_sock in out_socks.items():
            if id_out != id_in and name_is_valid(id_out):
                await out_sock.send(FetchDataStatus(updating=True))
        return False

    async def handle_fetch_lock_release(id_in: str, msg: FetchLockRelease):
        nonlocal version
        if msg.updated:
            version += 1
        if lock_owner != id_in:
            logger.error(
                "cannot release lock from non-owner. "
                f"lock owner: {lock_owner}, requestee: {id_in}"
            )
            await out_socks[id_in].send(FetchLockReleaseStatus(ok=False))
            return
        # fetch_lock.release()
        for id_out, out_sock in out_socks.items():
            if id_out != id_in and name_is_valid(id_out):
                status = FetchDataStatus(updating=False, version=version)
                logger.debug(f"send {status} to {id_out}")
                await out_sock.send(status)
        await out_socks[id_in].send(FetchLockReleaseStatus(ok=True))
        return False

    async def handle_msg(id_in: str, msg: Any):
        """
        if msg is unknown, simply relay the message back to the control.
        """
        await out_socks[id_in].send(msg)
        return False

    async def handle_signal(id_in, msg: Signal):
        logger.debug(f"received signal: {msg} from {id_in}")
        try:
            if isinstance(msg, Stop):
                return await handle_stop(id_in, msg)
            elif isinstance(msg, FetchLockAcquire):
                return await handle_fetch_lock_acquire(id_in, msg)
            elif isinstance(msg, FetchLockRelease):
                return await handle_fetch_lock_release(id_in, msg)
            elif isinstance(msg, PrefetchCompleted):
                return await handle_prefetch_completed(id_in, msg)
            elif isinstance(msg, StartRequest):
                return await handle_start_request(id_in, msg)
            else:
                return await handle_msg(id_in, msg)
        except Exception as e:
            print(e)

    async def control_loop():
        while True:
            socks = dict(await poller.poll(timeout=1))
            if not socks:
                continue
            for sock, type_ in socks.items():
                if type_ == zmq.POLLIN:
                    loop.create_task(
                        handle_signal(in_socks.inverse[sock], await sock.recv())
                    )

            done_tasks, _ = await asyncio.wait(
                asyncio.all_tasks(), return_when=asyncio.FIRST_COMPLETED, timeout=0.1
            )

            for task in done_tasks:
                if task.result() is True:
                    logger.debug("exiting controller")
                    return

    loop.set_debug(True)
    loop.run_until_complete(control_loop())
