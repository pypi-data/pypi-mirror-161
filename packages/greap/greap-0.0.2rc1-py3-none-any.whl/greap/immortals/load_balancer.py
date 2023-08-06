from typing import List
from itertools import cycle
import asyncio
import zmq
from ..zmq.socket import AsyncContext
from .signals import Stop


def socks_iter(socks):
    for sock in cycle(socks):
        yield sock


def LoadBalancer(
    id: str,
    root_dir: str,
    in_addr: str,
    out_addrs: List[str],
    in_ctrl_addr: str,
    out_ctrl_addr: str,
    **kwargs
):
    """
    This is the entry point of launching a load investedr. The load investedr
    load investeds traffice to replicas of the immortal.

    :params id: id of the immortal
    :params in_addr: the address that immortal gets data messages from
    :params out_addrs: the list of addresses that immortal pass data messages to
    :params in_ctrl_addr: the address of controller that immortal listens to
    to get control messages
    :params out_ctrl_addr: the address of the controller that immortal passes
    control messages to

    :returns: None
    """

    zmqctx = AsyncContext()
    in_sock = zmqctx.socket(zmq.PULL)
    in_sock.RCVTIMEO = 500
    in_sock.bind(in_addr)

    in_ctrl_sock = zmqctx.socket(zmq.PULL)
    in_ctrl_sock.bind(in_ctrl_addr)

    out_ctrl_sock = zmqctx.socket(zmq.PUSH)
    out_ctrl_sock.connect(out_ctrl_addr)
    stop_event = asyncio.Event()

    out_socks = []
    for oa in out_addrs:
        sock = zmqctx.socket(zmq.PUSH)
        sock.connect(oa)
        out_socks.append(sock)

    it = socks_iter(out_socks)

    loop = asyncio.get_event_loop()

    async def load_invested():
        nonlocal stop_event
        while not stop_event.is_set():
            try:
                data = await in_sock.recv()
            except zmq.error.Again:
                pass
            else:
                s = next(it)
                await s.send(data)

    async def in_ctrl_listen():
        nonlocal stop_event
        while True:
            msg = await in_ctrl_sock.recv()
            if isinstance(msg, Stop):
                stop_event.set()
                break

    t1 = loop.create_task(load_invested())
    t2 = loop.create_task(in_ctrl_listen())
    loop.run_until_complete(asyncio.wait([t1, t2], return_when=asyncio.FIRST_EXCEPTION))

    for sock in [in_sock, in_ctrl_sock, out_ctrl_sock] + out_socks:
        sock.setsockopt(zmq.LINGER, 0)
        sock.close()
    zmqctx.term()
