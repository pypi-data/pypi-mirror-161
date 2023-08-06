from collections import namedtuple
import pytz
from datetime import datetime
import inspect
import time
import yaml
from pathlib import Path
from typing import Union, Dict
from greap.import_utils import ImportFrom
from ..db import create_engine
from ..timer import Timer
from uuid import uuid1
from .address_pool import AddressPool


Field = namedtuple("Field", ["fields", "mandatory"])


SCHEMA = Field(
    {
        "backtest": Field(
            {
                "timer": Field(
                    {
                        "mode": Field(str, False),
                        "now": Field(str, False),
                        "scale": Field((float, int), False),
                        "fast_forward": Field(bool, False),
                    },
                    False,
                )
            },
            False,
        ),
        "services": Field(
            [
                Field(
                    {
                        "name": Field(str, True),
                        "immortal": Field(str, True),
                        "num_replicas": Field(int, False),
                        "params": Field(dict, False),
                        "log_level": Field(str, False),
                        "to": Field(list, False),
                    },
                    True,
                )
            ],
            False,
        ),
        "fetch": Field(
            {
                "start_at": Field(str, True),
                "interval": Field(int, True),
                "symbols": Field(list, True),
                "report_progress": Field(bool, False),
                "log_level": Field(str, False),
            },
            False,
        ),
        "controller": Field(
            {
                "log_level": Field(str, False),
            },
            False,
        ),
        "connector": Field(
            {
                "sink": Field(str, False),
                "log_level": Field(str, False),
            },
            False,
        ),
        "load_balancer": Field(
            {
                "log_level": Field(str, False),
            },
            False,
        ),
        "database_addr": Field(str, False),
    },
    True,
)


def verify_args(config: dict, schema: Field = SCHEMA, parent_key: str = "config"):
    keys = set()
    fields = schema.fields
    for key, value in config.items():
        assert key in fields, f"{parent_key} does not expect key {key}"
        keys.add(key)
        f = fields[key]
        if isinstance(f.fields, dict):
            verify_args(value, f, parent_key=key)
        elif isinstance(f.fields, list):
            assert isinstance(
                value, list
            ), f"{parent_key}'s {key} is expected to be a list, got {value}"
            for subconf in value:
                verify_args(subconf, f.fields[0], parent_key=key)
        elif isinstance(f.fields, type):
            assert isinstance(
                value, f.fields
            ), f"{parent_key}'s {key} is expected of type {f}, got {value}"
        elif isinstance(f.fields, tuple):
            assert isinstance(
                value, f.fields
            ), f"{parent_key}'s {key} is expected of one of types {f.fields}, got {value}"  # noqa: E501
        else:
            assert False, f"Unknown type, value: {value}, field: {f}"

    for name, field in fields.items():
        if field.mandatory and name not in keys:
            assert (
                False
            ), f"{parent_key}'s {name} is a mandatory field but is not provided"


def name_is_valid(name):
    return not name.startswith("load_balancer") and name not in {
        "server",
        "controller",
        "prefetcher",
    }


def load_config(path):

    config_path = path / "config.yml"
    if not config_path.is_file():
        raise ValueError("config.yml does not exist")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def _to_lb_name(name):
    return f"load_balancer-{name}"


def get_databse_addr(config, root_dir):
    database_addr = config.get(
        "database_addr", f"sqlite:////{{root_dir}}/storage-{uuid1()}.db"
    )
    database_addr = database_addr.format(root_dir=str(Path(root_dir).absolute()))
    print(database_addr)
    if not database_addr:
        raise ValueError("please provide a valid database addr")
    create_engine(database_addr)
    return database_addr


def compile_config(
    root_dir: Path,
    config: dict,
    backtest: bool,
    default_log_level: str,
    port: int,
):
    verify_args(config)
    from collections import defaultdict

    database_addr = get_databse_addr(config, root_dir)

    fetch_args = {
        "symbols": [],
        "source": "webull",
        "interval": 60,
        "start_at": str(datetime.now()),
        "log_level": default_log_level,
        "report_progress": False,
    }
    fetch_args.update(config.get("fetch", {}))
    fetch_args.setdefault("report_progress", False)

    controller_args = config.get("controller", {})

    connector_args = {
        "sink": "alpaca",
        "log_level": default_log_level,
        "sleep_interval": 1,
    }

    nytz = pytz.timezone("America/New_york")
    timer_args = {
        "now": datetime.now().astimezone(nytz).isoformat(),
        "mode": "auto",
        "scale": 1,
        "fast_forward": False,
        "now_actual": time.time(),
    }

    backtest_config = config.get("backtest", {})
    if backtest:
        timer_args.update(backtest_config.get("timer", {}))
        fetch_args["source"] = "backtest"
        connector_args["sink"] = "backtest"
        Timer.verify_args(**timer_args)

    with ImportFrom(root_dir, all=True) as gbv:
        new = defaultdict(dict)
        services = config.get("services", [])
        if not services:
            print(
                "WARNING: No service is found in config.yml. Only Prefetcher will run."
            )

        for info in services:
            name = info["name"]
            assert name_is_valid(name), (
                "service name should not be 'server', 'controller', 'prefetcher', "
                "or starts with 'load_balancer' as these are reserved."
            )
            num_replicas = info.get("num_replicas", 1)
            log_level = info.get("log_level", default_log_level)
            params = info.get("params", {})
            fn = gbv[info["immortal"]]
            assert "ctx" in inspect.signature(fn).parameters, (
                "invalid immortal function. ctx object needs to exist in "
                "immortal function parameters"
            )

            signature = inspect.signature(fn)
            try:
                s = signature.bind_partial(**params)
                fn_args, fn_kwargs = list(s.args), s.kwargs
            except TypeError as e:
                raise TypeError(
                    f'cannot bind parameters to immortal: {info["immortal"]}'
                ) from e

            if num_replicas > 1:
                lb_name = _to_lb_name(name)
                new[lb_name] = {
                    "type": "load_balancer",
                    "id": lb_name,
                    "root_dir": str(root_dir),
                    "workers": [],
                }

                for replica in range(num_replicas):
                    rid = f"{name}-{replica}"
                    new[rid].update(
                        {
                            "id": f"{name}-{replica}",
                            "type": "immortal",
                            "load_balancer": lb_name,
                            "to": info.get("to", []),
                            "fn_name": info["immortal"],
                            "fn_args": fn_args,
                            "fn_kwargs": fn_kwargs,
                            "root_dir": str(root_dir),
                            "database_addr": database_addr,
                            "log_level": log_level,
                            "timer_args": timer_args,
                            "source": "webull" if not backtest else "backtest",
                        }
                    )
                    new[_to_lb_name(name)]["workers"].append(rid)

            elif num_replicas == 1:
                new[name].update(
                    {
                        "id": name,
                        "type": "immortal",
                        "load_balancer": None,
                        "to": info.get("to", []),
                        "fn_name": info["immortal"],
                        "fn_args": fn_args,
                        "fn_kwargs": fn_kwargs,
                        "root_dir": str(root_dir),
                        "database_addr": database_addr,
                        "log_level": log_level,
                        "timer_args": timer_args,
                        "source": "webull" if not backtest else "backtest",
                    }
                )
            else:
                assert False, "num_replicas must be >=1"

    new["controller"] = {
        "type": "controller",
        "id": "controller",
        "timer_args": timer_args,
        "log_level": default_log_level,
    }
    new["controller"].update(controller_args)

    new["prefetcher"] = {
        "type": "prefetcher",
        "id": "prefetcher",
        "database_addr": database_addr,
        "timer_args": timer_args,
        **fetch_args,
    }

    new["connector"] = {
        "type": "connector",
        "id": "connector",
        "database_addr": database_addr,
        "timer_args": timer_args,
    }
    new["connector"].update(connector_args)

    new["server"] = {
        "type": "server",
        "id": "server",
        "database_addr": database_addr,
        "timer_args": timer_args,
        "port": port,
    }

    if backtest:
        new["bqpt"] = {
            "type": "backtest_quote_price_feeder",
            "id": "bqpt",
            "timer_args": timer_args,
            **fetch_args,  # TODO contains extra args; can be removed
        }

    Path(root_dir / ".greap").mkdir(parents=True, exist_ok=True)
    with open((root_dir / ".greap" / "compiled-config.yml"), "w") as f:
        yaml.safe_dump(dict(new), f)
    return new, timer_args


def create_routing_table(root_dir: Union[str, Path], config: Dict, pool: AddressPool):
    routing_table, in_addrs = {}, {}

    # First Pass - Populate in addrs, in ctrl addrs and out ctrl addrs
    for id, info in config.items():
        routing_table[id] = {}
        if info["type"] == "controller":
            continue

        if info["type"] in {
            "server",
            "prefetcher",
            "backtest_quote_price_feeder",
            "connector",
        }:
            routing_table[id]["in_ctrl_addr"] = pool.create(id)
            routing_table[id]["out_ctrl_addr"] = pool.create("controller")

        elif info["type"] == "load_balancer":
            routing_table[id]["in_addr"] = in_addrs[id] = pool.create(id)
            routing_table[id]["out_addrs"] = []
            routing_table[id]["in_ctrl_addr"] = pool.create(id)
            routing_table[id]["out_ctrl_addr"] = pool.create("controller")

        elif info["type"] == "immortal":
            routing_table[id]["in_addr"] = in_addrs[id] = pool.create(id)
            routing_table[id]["out_addrs"] = []
            routing_table[id]["in_ctrl_addr"] = pool.create(id)
            routing_table[id]["out_ctrl_addr"] = pool.create("controller")
        else:
            assert False, f"invalid service type, got {info['type']}"

    # Second Pass - Populate out addrs
    for id, info in config.items():
        if info["type"] == "load_balancer":
            for worker in info["workers"]:
                routing_table[id]["out_addrs"].append(in_addrs[worker])

        elif info["type"] == "immortal":
            for out in info["to"]:
                if out in config:
                    routing_table[id]["out_addrs"].append(in_addrs[out])
                elif _to_lb_name(out) in config:
                    routing_table[id]["out_addrs"].append(in_addrs[_to_lb_name(out)])
                else:
                    assert (
                        False
                    ), "immortal has neighther a load investedr (replicas > 1"
                    " nor a single instance with its own name (replica == 1)"

    routing_table["controller"]["in_addrs"] = {
        id: rt["out_ctrl_addr"]
        for id, rt in routing_table.items()
        if id != "controller"
    }

    routing_table["controller"]["out_addrs"] = {
        id: rt["in_ctrl_addr"] for id, rt in routing_table.items() if id != "controller"
    }

    # Third Pass - Populate roker Addrs
    source = config["prefetcher"]["source"]
    if source == "backtest":
        routing_table["bqpt"]["broker_addr"] = []

    for id, info in config.items():
        if info["type"] == "immortal":
            if source == "backtest":
                addr = pool.create(id)
                routing_table[id]["broker_addr"] = addr
                routing_table["bqpt"]["broker_addr"].append(addr)
            else:
                routing_table[id]["broker_addr"] = "wspush.webullbroker.com"

    with open((root_dir / ".greap" / "routing_table.yml"), "w") as f:
        yaml.dump(routing_table, f)

    return routing_table
