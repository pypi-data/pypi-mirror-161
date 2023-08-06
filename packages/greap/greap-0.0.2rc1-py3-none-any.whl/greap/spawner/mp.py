import signal
import time
from multiprocessing import Process
from ..logger import Logger
from ..timer import Timer

from .lib import (
    load_config,
    compile_config,
    create_routing_table,
)

from ..immortals.factory import immortal_factory


def spawn_immortals(
    config: dict, routing_table: dict, root_dir, timer_args: dict, backtest: bool
):
    alive = True
    procs = []

    for node, info in config.items():
        kwargs = {**info, **routing_table[node], "is_respawned": False}
        target = immortal_factory(kwargs.pop("type"))
        procs.append(Process(name=kwargs["id"], target=target, kwargs=kwargs))

    for proc in procs:
        proc.start()

    logger = Logger(name="main", timer=Timer(**timer_args), level="DEBUG")
    new_procs = []

    def handler(signum, frame):
        nonlocal procs, alive
        alive = False
        for proc in procs:
            proc.kill()

    signal.signal(signal.SIGALRM, handler)

    while alive:
        try:
            new_procs = []
            for proc in procs:
                if not proc.is_alive():
                    logger.debug(f"{proc.name} is not alive. collecting dead proc...")
                    proc.join()
                    logger.debug(f"{proc.name} is collected, respawning")
                    conf = config[proc.name]
                    kwargs = {**conf, **routing_table[proc.name], "is_respawned": True}
                    target = immortal_factory(kwargs.pop("type"))
                    new_proc = Process(name=proc.name, target=target, kwargs=kwargs)
                    new_proc.start()
                    new_procs.append(new_proc)
                else:
                    new_procs.append(proc)

            procs = new_procs
        except (KeyboardInterrupt, SystemExit):
            for proc in procs:
                proc.kill()
            for proc in new_procs:
                proc.kill()
            break

        time.sleep(1)


def spawn(root_dir: str, default_log_level: str, backtest: bool, port: int):
    from pathlib import Path

    root_dir = Path(root_dir)
    config = load_config(root_dir)
    config, timer_args = compile_config(
        root_dir, config, backtest, default_log_level, port
    )
    from .address_pool import LocalAddressPool

    pool = LocalAddressPool()
    routing_table = create_routing_table(root_dir, config, pool)
    spawn_immortals(config, routing_table, root_dir, timer_args, backtest)
