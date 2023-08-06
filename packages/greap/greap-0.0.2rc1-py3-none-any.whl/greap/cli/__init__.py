import json
from typing import List, Dict
import os
import click
from pathlib import Path
from datetime import datetime

from greap.spawner import spawn_factory
from greap.logger.rich_utils import RichGroup, RichCommand
from greap.backtest import collect
from greap.docker import DockerBuilder
from greap.spawner.lib import load_config

from greap.immortals.base import Immortal
from greap.immortals.controller import Controller
from greap.immortals.connector import Connector
from greap.immortals.load_balancer import LoadBalancer
from greap.immortals.backtest_quote_price_feeder import BacktestQuotePriceFeeder
from greap.immortals.prefetcher import Prefetcher

# patch click usage exception
from .patch import *  # noqa: F401,F403


@click.group(cls=RichGroup)
# @click.option('--testing', help='test this framework')
def cli():
    """\
[i b magenta]Greap[/i b magenta] is simple but powerful library for building scalable trading systems.
"""
    pass


@cli.command(cls=RichCommand)
@click.argument("path", default=os.getcwd())
@click.option(
    "--on",
    default="mp",
    help="The platform to run the system on. The default is mp, which stands for multiprocessing.",
)
@click.option(
    "--default-log-level",
    default="INFO",
    help="The default level of logging. This will be overriden by the `log_level` specify in each immortal's config",
)
@click.option("--port", default=80, help="The port to host the server on")
def run(path, on, default_log_level, port):
    """\
Runs the holistic greap system with the resources in the directory specified by PATH.
"""
    spawn_factory(on)(path, default_log_level, False, port)


@cli.command(cls=RichCommand)
@click.argument("path", default=os.getcwd())
@click.option(
    "--on",
    default="mp",
    help="The platform to backtest the system on. The default is mp, which stands for multiprocessing.",
)
@click.option(
    "--default-log-level",
    default="INFO",
    help="The default level of logging. This will be overriden by the `log_level` specify in each immortal's config",
)
@click.option("--port", default=80, help="The port to host the server on")
def backtest(path, on, default_log_level, port):
    """\
Runs the holistic greap system with the resources in the directory specified by PATH, with backtest data.
"""
    backtest_path = Path(path) / "backtest.db"
    if not backtest_path.exists():
        raise Exception(
            "backtest db does not exist, "
            "please use collect-backtest-data command to collect backtest data first"
        )
    os.environ["BACKTEST_DATA_PATH"] = str(backtest_path)
    spawn_factory(on)(path, default_log_level, True, port)


@cli.command(cls=RichCommand)
@click.argument("path")
@click.option(
    "--output-path",
    default=None,
    help="The path to output collected backtest data",
)
def collect_backtest_data(path, output_path):
    """\
Collect backtest data of the given symbols starting at the given time.
"""
    root_dir = Path(path)
    output_path = root_dir / "backtest.db"
    config = load_config(root_dir)
    symbols = config["fetch"]["symbols"]
    start_at = config["fetch"]["start_at"]
    end_at = datetime.now()
    collect(symbols, output_path, start_at, end_at)


@cli.command(cls=RichCommand)
@click.argument("path")
@click.option("--nocache", is_flag=True, help="Whether to build Docker with no cache")
@click.option("--x86", is_flag=True, help="Whether to build Docker with x86")
def build(path, nocache, x86: bool):
    """\
Builds a greap docker image for the given directory.
"""
    DockerBuilder(path).login().build(nocache, x86).push()


def json_loads(ctx, param, value):
    if value is not None:
        return json.loads(value)


@cli.command(
    cls=RichCommand,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.option("--id", help="The id of the immortal", callback=json_loads)
@click.option("--root_dir", help="The root directory", callback=json_loads)
@click.option(
    "--fn_name", help="The name of the immortal function", callback=json_loads
)
@click.option(
    "--in_addr",
    help="The address which is bound to for receiving data messages",
    callback=json_loads,
)
@click.option(
    "--out_addrs",
    help="The list of addresses to conenct to for sending data messages",
    callback=json_loads,
)
@click.option(
    "--in_ctrl_addr",
    help="The addresses which is bound to for receving control messages",
    callback=json_loads,
)
@click.option(
    "--out_ctrl_addr",
    help="The addresses which is connected to for receving control messages",
    callback=json_loads,
)
@click.option(
    "--database_addr",
    help="The addresses which is connected to for receving control messages",
    callback=json_loads,
)
@click.option(
    "--broker_addr",
    help="The broker address",
    callback=json_loads,
)
@click.option("--timer_args", help="The argument to timer object", callback=json_loads)
@click.option(
    "--source", help="The source where data is fetched from", callback=json_loads
)
@click.option(
    "--fn_args",
    help="The list of arguments to be passed to the immortal",
    callback=json_loads,
)
@click.option(
    "--fn_kwargs",
    help="The dict of arguments to be passed to the immortal",
    callback=json_loads,
)
@click.option("--log_level", help="The log level", callback=json_loads)
@click.pass_context
def run_immortal(
    ctx,
    id,
    root_dir,
    fn_name,
    in_addr,
    out_addrs,
    in_ctrl_addr,
    out_ctrl_addr,
    database_addr,
    broker_addr,
    timer_args,
    source,
    fn_args,
    fn_kwargs,
    log_level,
):
    """\
Runs an immortal with the given addresses and on the given platform.
"""
    print("timer_args", timer_args)
    # import pdb

    # pdb.set_trace()
    Immortal(
        id,
        root_dir,
        fn_name,
        in_addr,
        out_addrs,
        in_ctrl_addr,
        out_ctrl_addr,
        database_addr,
        timer_args,
        source,
        broker_addr,
        fn_args,
        fn_kwargs,
        log_level,
    )


@cli.command(
    cls=RichCommand,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.option("--id", help="The id of the immortal", callback=json_loads)
@click.option(
    "--in_addrs",
    help="The lists of addresses to bind to for receiving incoming control messages",
    callback=json_loads,
)
@click.option(
    "--out_addrs",
    help="The list of addresses to conenct to for sending outgoing control messages",
    callback=json_loads,
)
@click.option("--timer_args", help="The argument to timer object", callback=json_loads)
@click.option("--log_level", help="The log level", callback=json_loads)
@click.pass_context
def run_controller(ctx, id, in_addrs, out_addrs, timer_args, log_level):
    """\
Runs the controller with the given addresses and on the given platform.
"""
    print("timer_args", timer_args)
    Controller(
        id,
        in_addrs,
        out_addrs,
        timer_args,
        log_level,
    )


@cli.command(
    cls=RichCommand,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.option("--id", help="The id of the load balanacer", callback=json_loads)
@click.option("--root_dir", help="The root directory", callback=json_loads)
@click.option(
    "--in_addr",
    help="The address to bind to for receiving incoming data messages",
    callback=json_loads,
)
@click.option(
    "--out_addrs",
    help="The list of addresses to conenct to for sending outgoing data messages",
    callback=json_loads,
)
@click.option(
    "--in_ctrl_addr",
    help="The address to bind to for receiving incoming control messages",
    callback=json_loads,
)
@click.option(
    "--out_ctrl_addr",
    help="The list of addresses to conenct to for sending outgoing control messages",
    callback=json_loads,
)
@click.pass_context
def run_load_balancer(
    ctx, id, root_dir, in_addr, out_addrs, in_ctrl_addr, out_ctrl_addr
):
    """\
Runs the load balancer with the given addresses and on the given platform.
"""
    LoadBalancer(id, root_dir, in_addr, out_addrs, in_ctrl_addr, out_ctrl_addr)


@cli.command(
    cls=RichCommand,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.option("--id", help="The id of the load balanacer", callback=json_loads)
@click.option("--database_addr", help="The database address", callback=json_loads)
@click.option(
    "--timer_args", help="The arguments to the timer object", callback=json_loads
)
@click.option("--sink", help="The api to place order with", callback=json_loads)
@click.option(
    "--sleep_interval",
    help="The duration to sleep for an interval",
    callback=json_loads,
)
@click.pass_context
def run_connector(
    ctx,
    id,
    database_addr,
    timer_args,
    sink,
    sleep_interval,
):
    """\
Runs the connector with the given addresses and on the given platform.
"""
    print("timer_args", timer_args)
    Connector(
        id,
        database_addr,
        timer_args,
        sink,
        sleep_interval,
    )


@cli.command(
    cls=RichCommand,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.option("--id", help="The id of the load balanacer", callback=json_loads)
@click.option(
    "--in_ctrl_addr", help="The address of incoming ctrl messages", callback=json_loads
)
@click.option(
    "--out_ctrl_addr", help="The address of outgoing ctrl messages", callback=json_loads
)
@click.option("--database_addr", help="The address of database", callback=json_loads)
@click.option("--interval", help="The interval between each fetch", callback=json_loads)
@click.option("--start_at", help="The interval between each fetch", callback=json_loads)
@click.option("--symbols", help="The symbols to fetch", callback=json_loads)
@click.option(
    "--timer_args", help="The arguments to the timer object", callback=json_loads
)
@click.option(
    "--source", help="The source from where data is fetched", callback=json_loads
)
@click.option(
    "--report_progress", help="Whether to report progress", callback=json_loads
)
@click.option("--log_level", help="Whether to report progress", callback=json_loads)
@click.pass_context
def run_prefetcher(
    ctx,
    id,
    in_ctrl_addr,
    out_ctrl_addr,
    database_addr,
    interval,
    start_at,
    symbols,
    timer_args,
    source,
    report_progress,
    log_level,
):
    """\
Runs the prefetcher with the given addresses and on the given platform.
"""
    print("timer_args", timer_args)
    Prefetcher(
        id,
        in_ctrl_addr,
        out_ctrl_addr,
        database_addr,
        interval,
        start_at,
        symbols,
        timer_args,
        source,
        report_progress,
        log_level,
    )


@cli.command(
    cls=RichCommand,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.option("--id", help="The id of the load balancer", callback=json_loads)
@click.option(
    "--in_ctrl_addr", help="The address of incoming ctrl messages", callback=json_loads
)
@click.option(
    "--out_ctrl_addr", help="The address of outgoing ctrl messages", callback=json_loads
)
@click.option("--start_at", help="The interval between each fetch", callback=json_loads)
@click.option("--symbols", help="The symbols to fetch", callback=json_loads)
@click.option(
    "--timer_args", help="The arguments to the timer object", callback=json_loads
)
@click.option("--broker_addr", help="The address of broker", callback=json_loads)
@click.option("--log_level", help="Whether to report progress", callback=json_loads)
@click.pass_context
def run_backtest_quote_price_feeder(
    ctx,
    id: str,
    in_ctrl_addr: str,
    out_ctrl_addr: str,
    start_at: str,
    symbols: List[str],
    timer_args: Dict,
    broker_addr: List[str],
    log_level: str,
):
    print("timer_args", timer_args)
    BacktestQuotePriceFeeder(
        id,
        in_ctrl_addr,
        out_ctrl_addr,
        start_at,
        symbols,
        timer_args,
        broker_addr,
        log_level,
    )


@cli.command(cls=RichCommand)
def help():
    """\
Show this help text.\
"""
    pass
