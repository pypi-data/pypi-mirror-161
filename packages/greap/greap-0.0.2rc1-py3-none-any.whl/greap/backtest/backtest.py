import tempfile
import shutil
from typing import Union
from pathlib import Path
from datetime import datetime
import asyncio
from greap.immortals.prefetcher import fetch
from greap.timer import Timer
from greap.models import Price, Symbol, SQLModel
from greap.logger import Logger
from greap.clients import get_historic_prices_factory
from sqlmodel import create_engine, Session


def collect(
    symbols: list,
    output_path: str,
    start_at: Union[str, datetime],
    end_at: Union[str, datetime],
):

    loop = asyncio.get_event_loop()
    tmp_path = tempfile.NamedTemporaryFile(suffix=".db")
    conn = create_engine(f"sqlite:///{Path(tmp_path.name).absolute()}")
    timer = Timer()

    if isinstance(start_at, str):
        start_at = datetime.fromisoformat(start_at)

    if isinstance(end_at, str):
        end_at = datetime.fromisoformat(end_at)

    api = get_historic_prices_factory("webull")

    schemas = {}
    for symbol in symbols:
        cls = type(symbol, (Price,), {}, table=True)
        schemas[symbol] = cls

    SQLModel.metadata.create_all(conn)
    with Session(conn) as sess:
        for symbol in symbols:
            sess.add(Symbol(name=symbol, start_at=start_at, end_at=start_at))
        sess.commit()

    SQLModel.metadata.create_all(conn)

    logger = Logger(id, timer=timer, level="INFO")

    loop.run_until_complete(
        fetch(
            api,
            loop,
            conn,
            schemas,
            start_at,
            timer,
            logger,
            "webull",
            True,
            True,
        )
    )
    shutil.copy(tmp_path.name, output_path)
