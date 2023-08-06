import warnings
from contextlib import asynccontextmanager
import asyncio
from typing import Optional, List, Dict, Callable, Union

import zmq

from ..logger import Logger
from ..zmq.socket import AsyncContext
from ..import_utils import ImportFrom
from .signals import (
    Signal,
    StartRequest,
    ReadyToStart,
    DisableOpen,
    EnableOpen,
    FetchDataStatus,
    Stop,
)

# from .event import OrEvent
from ..api import ExchangeAPI
from ..timer import Timer
from .validator import Validator
from ..types import PrimitiveU, DictSerializable
from ..exceptions import StopImmortal


class ImmortalContext:
    """
    The context object that is passed into immortal which contains useful objects
    such as logger, api and timer.

    :param name: The name of the immortal
    :param in_addr: The address of the incoming data packet socket
    :param out_addrs: The addresses of the outgoing data packet sockets
    :param in_ctrl_addr: The addresses of the incoming control packet sockets
    :param out_ctrl_addr: The addresses of the outgoing control packet sockets
    :param database_addr: The address of database
    :param fn: The name of the immortal function to use
    :param fn_args: The list of (primitive) arguments to be passed to the immortal
    :param fn_kwargs: The dict of (primitive) arguments to be passed to the immortal
    :param timer: The parameters for timer object
    :param source: The source to fetch data from
    :param broker_addr: The address of broker
    """

    DB_UPDATE = 0b1
    TRIGGERED = 0b111

    def __init__(
        self,
        name: str,
        in_addr: str,
        out_addrs: List[str],
        in_ctrl_addr: str,
        out_ctrl_addr: str,
        database_addr: str,
        fn: str,
        log_level: str,
        fn_args: Optional[List[PrimitiveU]],
        fn_kwargs: Optional[Dict[str, PrimitiveU]],
        timer: Timer,
        source: str,
        broker_addr: str,
        # broker_addr: str = 'test.mosquitto.org',
    ):
        self._broker_addr = broker_addr
        self.validator = Validator()
        self.timer = timer
        print("before init context")
        self._zmqctx = AsyncContext()
        print("before init socket")
        (
            self.in_sock,
            self.out_socks,
            self.in_ctrl_sock,
            self.out_ctrl_sock,
        ) = self._init_sockets(in_addr, out_addrs, in_ctrl_addr, out_ctrl_addr)
        print("after init socket")

        # synchronization events
        self._stop_event = asyncio.Event()
        self._allow_open_event = asyncio.Event()
        self._start_event = asyncio.Event()
        self._finished_updating_event = asyncio.Event()
        self._dirty_event = asyncio.Event()
        self._trigger_event = asyncio.Event()

        # queue for recieving quote prices on mqtt subscribe
        self.quote_prices_queue = asyncio.Queue()

        self.version = -1
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        self._loop = asyncio.get_event_loop()

        if log_level == "DEBUG":
            self._loop.set_debug(True)

        self._fn_args = fn_args or []
        self._fn_kwargs = fn_kwargs or {}
        self._exc = None
        self._force_retry_after = None

        # public expose APIs
        self.fn = fn

        self.logger = Logger(name, timer, level=log_level)
        self.api = ExchangeAPI(
            validator=self.validator,
            can_open=self.can_open,
            get_version=self.get_version,
            is_updating=self.is_updating,
            db_conn=database_addr,
            timer=self.timer,
            logger=self.logger,
            source=source,
        )
        self.sleep = self.timer.sleep
        self.maintain_interval = self.timer.maintain_interval
        self.now = self.timer.now
        self._triggers: List[Callable[..., bool]] = []
        self._source = source

        # enable for instance self.api.price.take(10) -> self.price.take(10)
        for name, api in self.api.items():
            setattr(self, name, api)

    def add_trigger(self, cb: Callable[..., bool]):
        self._triggers.append(cb)

    async def get(self) -> Union[PrimitiveU, DictSerializable]:
        while self:
            try:
                return await self.in_sock.recv()
            except zmq.error.Again:
                pass

    async def put(self, item: PrimitiveU):
        if item is None:
            raise ValueError("None is not an accepted value! Try using other sentinels")
        for s in self.out_socks:
            await s.send(item)

    def _init_sockets(
        self, in_addr: str, out_addrs: List[str], in_ctrl_addr: str, out_ctrl_addr: str
    ):
        in_sock = self._zmqctx.socket(zmq.PULL)
        in_sock.RCVTIMEO = 500
        in_sock.bind(in_addr)

        out_socks = []
        for oa in out_addrs:
            sock = self._zmqctx.socket(zmq.PUSH)
            sock.connect(oa)
            out_socks.append(sock)

        in_ctrl_sock = self._zmqctx.socket(zmq.PULL)
        in_ctrl_sock.bind(in_ctrl_addr)

        out_ctrl_sock = self._zmqctx.socket(zmq.PUSH)
        out_ctrl_sock.connect(out_ctrl_addr)

        return in_sock, out_socks, in_ctrl_sock, out_ctrl_sock

    async def immortal_fn(self):
        try:
            await self.fn(self, *self._fn_args, **self._fn_kwargs)
        except Exception as e:
            print(e)
            raise
        else:
            # gracefully end immortal; set stop event after finish iteration raise stop
            raise StopImmortal()

    async def _in_ctrl_listen(self):
        while True:
            if not self._start_event.is_set():
                print(f"sent {StartRequest()}...")
                await self.out_ctrl_sock.send(StartRequest())
                await asyncio.sleep(1)
            msg = await self.in_ctrl_sock.recv(noblock=True)
            self._handle_signal(msg)
            await asyncio.sleep(0.5)

    async def _wait_for_ready(self):
        # await OrEvent(self._start_event, self._stop_event, module=asyncio).wait()
        while True:
            print("wait for ready", self._start_event, self._stop_event)
            if self._start_event.is_set():
                return
            if self._stop_event.is_set():
                return
            await asyncio.sleep(0.5)

    @asynccontextmanager
    async def wait_for(
        self,
        *,
        triggered: bool = True,
        db_update: bool = False,
        mode: str = "any",
    ):
        if self._force_retry_after is not None:
            await self.sleep(self._force_retry_after)
            self._force_retry_after = None
            yield
            return

        tasks = []

        if db_update:
            tasks.append(self._dirty_event.wait())

        if triggered:
            tasks.append(self._trigger_event.wait())

        if mode == "any":
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        elif mode == "all":
            await asyncio.gather(*tasks)
        else:
            raise ValueError("invalid mode; only any or all is accepted")

        yield

        if db_update:
            self._dirty_event.clear()

        if triggered:
            self._trigger_event.clear()

    def skip_wait_and_retry_after(self, seconds: int):
        self._force_retry_after = seconds

    def _handle_signal(self, msg: Signal):
        if msg is not None:
            self.logger.debug(f"received signal {msg}")
        if isinstance(msg, ReadyToStart):
            self._start_event.set()
        if isinstance(msg, DisableOpen):
            self._allow_open_event.clear()
        if isinstance(msg, EnableOpen):
            self._allow_open_event.set()
        if isinstance(msg, (Exception, Stop)):
            self._stop_event.set()
        if isinstance(msg, Exception):
            self._exc = msg
        if isinstance(msg, FetchDataStatus):
            if msg.updating:
                self._finished_updating_event.clear()
            else:
                if self.version < msg.version:
                    self._dirty_event.set()
                self.version = msg.version
                self.logger.debug("set finished updating")
                self._finished_updating_event.set()

    def is_alive(self) -> bool:
        """
        Check if context is still alive. If any of immortals sent an
        exception to the controller, controller will forward exception
        to all other immortals. Upon recieving an Exception from the
        control, stop event will be set

        :return: return if the context is still alive
        """
        return not self._stop_event.is_set()

    def can_open(self) -> bool:
        """
        Check if context allows for opening position. this event is
        set when an http request is send to enable/disable opening position.
        to the controller.

        :return: return if the context allows for opening position
        """
        return not self._allow_open_event.is_set()

    def __bool__(self):
        return self.is_alive()

    def release(self):
        """
        Release the zmq context and all sockets used.
        """
        for sock in [
            self.in_ctrl_sock,
            self.in_sock,
            self.out_ctrl_sock,
            *self.out_socks,
        ]:
            sock.setsockopt(zmq.LINGER, 0)
            sock.close()
        self._zmqctx.term()

    def is_updating(self):
        return not self._finished_updating_event.is_set()

    def get_version(self):
        return self.version

    async def _mqtt_subscribe(self):
        """
        This method subscribes to mosquitto web socket client
        and puts messages recieved onto `quote_prices_queue`.
        """
        if self._source == "webull":
            from ..clients.wb import quote_price_subscribe

        elif self._source == "backtest":
            from ..clients.backtest import quote_price_subscribe

        else:
            raise ValueError("unknown source type")

        await quote_price_subscribe(
            self.quote_prices_queue,
            self.is_alive,
            self._broker_addr,
        )

    async def _checking_triggers(self):
        """
        This method gets messages in `quote_prices_queue`
        and call any triggers user has added to the context.
        if trigger returns true, trigger event is set. And
        depending on whether `wait_for` waits for `trigger_event`,
        ends the wait to unblock immortal logic.
        """
        while msg := await self.quote_prices_queue.get():
            if msg[1] <= self.now() << 1:
                continue

            for trig in self._triggers:
                if trig(self, *msg):
                    self._trigger_event.set()


def Immortal(
    id: str,
    root_dir: str,
    fn_name: str,
    in_addr: str,
    out_addrs: List[str],
    in_ctrl_addr: str,
    out_ctrl_addr: str,
    database_addr: str,
    timer_args: Dict,
    source: str,
    broker_addr: str,
    fn_args: Optional[List[PrimitiveU]] = None,
    fn_kwargs: Optional[Dict[str, PrimitiveU]] = None,
    log_level: str = "INFO",
    **kwargs,
):
    """
    This is the entry point of launching an immortal.
    This function launches two tasks. One for running the business logic defined
    users' provided function. One for listening to control signal.

    :params id: id of the immortal
    :params root_dir: the root directory containing all user defined immortals and
    auxilary methods and classes
    :params fn_name: the name of the immortal function
    :params in_addr: the address that immortal gets data messages from
    :params out_addrs: the list of addresses that immortal pass data messages to
    :params in_ctrl_addr: the address of controller that immortal listens to
    to get control messages
    :params out_ctrl_addr: the address of the controller that immortal passes
    control messages to
    :param database_addr: the address of database
    :param timer_args: the arguments to timer object
    :param source: the source where data is fetched from
    :param fn_args: the list of arguments to immoratl function
    :param fn_kwargs: the dict of arguments to immoratl function

    :returns: None
    """
    print("before Timer")
    timer = Timer(**timer_args)
    print("after Timer")
    ctx, exception = None, None
    print("before with ImportFrom")

    with ImportFrom(root_dir, fn_name) as fn:
        print("before immortal context")
        ctx = ImmortalContext(
            id,
            in_addr,
            out_addrs,
            in_ctrl_addr,
            out_ctrl_addr,
            database_addr,
            fn,
            log_level,
            fn_args,
            fn_kwargs,
            timer,
            source,
            broker_addr,
        )

        t1 = ctx._loop.create_task(ctx._in_ctrl_listen(), name=f"{id}-ctrl")

        done, pending = ctx._loop.run_until_complete(
            asyncio.wait([t1], timeout=2, return_when=asyncio.FIRST_COMPLETED)
        )

        for task in done | pending:
            try:
                exception = task.exception()
            except asyncio.exceptions.InvalidStateError:
                pass

        if exception:
            ctx.logger.debug(f"raise exception {exception} from immortal")
            raise exception

        ctx._loop.run_until_complete(ctx._wait_for_ready())
        t2 = ctx._loop.create_task(ctx.immortal_fn(), name=f"{id}-immortal")
        t3 = ctx._loop.create_task(ctx._mqtt_subscribe(), name=f"{id}-mqtt-subscribe")
        t4 = ctx._loop.create_task(
            ctx._checking_triggers(), name=f"{id}-checking_triggers"
        )
        done, pending = ctx._loop.run_until_complete(
            asyncio.wait([t1, t2, t3, t4], return_when=asyncio.FIRST_EXCEPTION)
        )
        print(done, pending)
        for task in done | pending:
            try:
                exception = task.exception()
                if exception:
                    break
            except asyncio.exceptions.InvalidStateError:
                pass

        ctx.release()

    timer.close()
    if exception:
        ctx.logger.debug(f"raise exception {exception} from immortal")
        raise exception
