from typing import Callable, Union, Optional
from dataclasses import dataclass
from dictdiffer import diff
from sqlmodel import SQLModel
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from .timer import Timer
from sqlalchemy import select


class DbDiffSubscriber:
    @dataclass(frozen=True)
    class Query:
        cls: SQLModel
        primary_key: sqlalchemy.orm.attributes.InstrumentedAttribute
        attr: sqlalchemy.orm.attributes.InstrumentedAttribute
        callback: Callable

    def __init__(
        self,
        conn: Union[str, sqlalchemy.engine.base.Engine],
        timer: Timer,
        stop: Optional[bool] = None,
        sleep_interval: float = 1,
    ):
        self._conn = create_async_engine(conn) if isinstance(conn, str) else conn
        self._data = {}
        self._queries = []
        self._sleep_interval = sleep_interval
        self._stop = False
        self._timer = timer
        self._session = AsyncSession(self._conn)

    def observe(
        self,
        cls: SQLModel,
        primary_key: sqlalchemy.orm.attributes.InstrumentedAttribute,
        attr: Optional[sqlalchemy.orm.attributes.InstrumentedAttribute] = None,
    ):
        def wrapper(method):
            self._queries.append(
                DbDiffSubscriber.Query(
                    cls=cls, primary_key=primary_key, attr=attr, callback=method
                )
            )
            return method

        return wrapper

    async def run_event_loop(self):
        while not self._stop:
            for query in self._queries:
                async with self._session:
                    try:
                        if query.attr is None:
                            new_data = {
                                pk: None
                                for (pk,) in await self._session.execute(
                                    select(query.primary_key)
                                )
                            }
                        else:
                            new_data = {
                                pk: attr
                                for (pk, attr) in await self._session.execute(
                                    select(query.primary_key, query.attr)
                                )
                            }
                    except sqlalchemy.exc.OperationalError:
                        new_data = {}
                old_data = self._data.get(query, {})
                args = {"old": {}, "new": {}}
                di = list(diff(old_data, new_data))
                for d in di:
                    if d[0] == "add":
                        args["old"].update({d[2][0][0]: None})
                        args["new"].update({d[2][0][0]: d[2][0][1]})
                    elif d[0] == "change":
                        args["old"].update({d[1][0]: d[2][0]})
                        args["new"].update({d[1][0]: d[2][1]})

                if args["new"] or args["old"]:
                    await query.callback(**args)
                self._data[query] = new_data
            await self._timer.sleep(seconds=self._sleep_interval)
