import warnings
import inspect
import numpy as np
import itertools
from math import isnan
from bisect import bisect_left
from datetime import timedelta
from operator import itemgetter
from datetime import datetime
from abc import ABC
from typing import Optional, Callable, List, Dict, Union, Tuple

from sqlmodel import (
    Table,
    SQLModel,
    Session,
    update,
    bindparam,
    func,
    and_,
)
from functools import partial
import sqlalchemy
from numba import typeof
from numba.core import types
from numba.typed import Dict as nDict

from .models import (
    Price,
    Position,
    PositionTuple,
    ZipPositions,
    Symbol,
    Datum,
    Signal,
    PositionSelectRequest,
    trange,
    StrTag,
    NumberTag,
    BoolTag,
    to_sqlalchemy_query,
)

from .types import PriceTimeDict
from .timer import Timer
from .logger import Logger
from .immortals.validator import Validator
from .profiler import timeit
from .constants import ReturnType
from .numba.optimize import accumulate_profits, accumulate_investeds
from .cache import timestamp
from .db import create_engine


def average(li):
    return sum(l) / len(li) if l else float("nan")


def downsample(signal, num_points):
    if len(signal) >= 2:
        interval = max(len(signal) // num_points, 1)
        middle = signal[1:-1]
        middle.reverse()
        middle = middle[:: int(max(1, interval))]
        middle.reverse()
        signal = [signal[0]] + middle + [signal[-1]]
    return signal


def zip_positions(
    list_of_tuples: List[Tuple],
):
    float_fields: Tuple[str] = (
        "quantity",
        "open_price",
        "close_price",
        "open_at",
        "close_at",
    )
    str_fields: Tuple[str] = ("symbol",)

    if len(list_of_tuples) == 0:
        return ZipPositions(
            ids=None,
            symbol_hashes=np.empty(0, dtype=np.int64),
            symbols=[],
            positions=None,
            statuss=None,
            quantitys=np.empty(0, dtype=np.float64),
            open_prices=np.empty(0, dtype=np.float64),
            close_prices=np.empty(0, dtype=np.float64),
            open_ats=np.empty(0, dtype=np.float64),
            close_ats=np.empty(0, dtype=np.float64),
            updated_ats=None,
            tags=None,
        )

    arr = list(zip(*list_of_tuples))

    float_indices = [f in float_fields for f in PositionTuple._fields]
    floats = list(itertools.compress(arr, float_indices))
    floats = list(map(partial(np.array, dtype=np.float64), floats))

    str_indices = [f in str_fields for f in PositionTuple._fields]
    strs = list(itertools.compress(arr, str_indices))
    ints = list(map(np.array, [list(map(hash, s)) for s in strs]))

    return ZipPositions(
        ids=None,
        symbol_hashes=ints[0],
        symbols=strs[0],
        positions=None,
        statuss=None,
        quantitys=floats[0],
        open_prices=floats[1],
        close_prices=floats[2],
        open_ats=floats[3],
        close_ats=floats[4],
        updated_ats=None,
        tags=None,
    )


def ensure_value(values, null_value):
    return [val if val is not None else null_value for value in values]


class defaultkeydict(dict):
    def __init__(self, factory: Callable[[str], Table]):
        self.factory = factory

    def __missing__(self, key: str):
        self[key] = self.factory(key)
        return self[key]


def validate_atomic(method):
    def wrapper(self, *args, **kwargs):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller_name = calframe[1].filename + ":" + str(calframe[1].lineno)
        self.validator.add_version(
            "before", self.get_version(), caller_name=caller_name
        )
        self.validator.add_updating_status(
            "before", self.is_updating(), caller_name=caller_name
        )
        res = method(self, *args, **kwargs)
        self.validator.add_version("after", self.get_version(), caller_name=caller_name)
        self.validator.add_updating_status(
            "after", self.is_updating(), caller_name=caller_name
        )
        return res

    return wrapper


class APIPlugin(ABC):
    def __init__(
        self,
        api: "ExchangeAPI",
        conn: Union[str, sqlalchemy.engine.base.Engine],
        timer: Timer,
        logger: Logger,
        validator: Validator,
        get_version: Callable,
        is_updating: Callable,
    ):
        if isinstance(conn, str):
            self._conn = create_engine(conn)
            try:
                SQLModel.metadata.create_all(self._conn)
            except sqlalchemy.exc.OperationalError:
                pass
        else:
            self._conn = conn
        self._timer = timer
        self._logger = logger
        self.validator = validator
        self.get_version = get_version
        self.is_updating = is_updating
        self.api = api


class PricePlugin(APIPlugin):
    def __init__(self, source, *args, **kwargs):
        super(PricePlugin, self).__init__(*args, **kwargs)

        def factory(symbol):
            with warnings.catch_warnings():
                # ignore sql warning for redeclaring class
                warnings.simplefilter("ignore")
                return type(
                    symbol,
                    (Price,),
                    {"__table_args__": {"extend_existing": True}},
                    table=True,
                )

        self._symbol_to_prices = defaultkeydict(factory)

        try:
            SQLModel.metadata.create_all(self._conn)
        except sqlalchemy.exc.OperationalError:
            pass

        from .clients import get_quote_price_factory

        self._quote_price_api = get_quote_price_factory(source)

    @validate_atomic
    def _take_last(
        self,
        *,
        symbol: str,
        count: int,
        end_at: datetime,
        type: str = "close",
        with_time: bool = False,
        strict=True,
    ):
        """
        This takes the last ``n`` points of stock with the given ``symbol``

        :param symbol: the name of symbol to take
        :param n: last n points to get
        """
        end_at <<= 0
        with Session(self._conn) as sess:
            res = list(
                map(
                    itemgetter(*([0, 1] if with_time else [1])),
                    sess.query(
                        self._symbol_to_prices[symbol].time,
                        getattr(self._symbol_to_prices[symbol], type),
                    )
                    .where(
                        self._symbol_to_prices[symbol].time <= (end_at or datetime.max)
                    )
                    .order_by(self._symbol_to_prices[symbol].time.desc())
                    .limit(count),
                )
            )
            if strict and len(res) != count:
                self.validator.add_error(
                    f"cannot get {count} price(s) for symbol {symbol}"
                )
            return list(reversed(res))

    @validate_atomic
    def take(
        self,
        *,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        symbol: str,
        type: str = "close",
        return_type: ReturnType = ReturnType.LIST,
    ) -> Union[List[Datum], PriceTimeDict]:

        with Session(self._conn) as sess:
            q = sess.query(
                self._symbol_to_prices[symbol].time,
                getattr(self._symbol_to_prices[symbol], type),
            )
            if start_at is not None:
                q = q.where(self._symbol_to_prices[symbol].time >= start_at)

            if end_at is not None:
                q = q.where(self._symbol_to_prices[symbol].time <= end_at)

            q = q.order_by(self._symbol_to_prices[symbol].time.asc())

            if return_type == ReturnType.DICT:
                return {t: p for t, p in q}

            elif return_type == ReturnType.LIST:
                times, prices = [], []
                for item in q:
                    times.append(item[0])
                    prices.append(item[1])
                return times, prices
            else:
                raise NotImplementedError("not implemented")

    @validate_atomic
    def take_at(
        self,
        *,
        symbol: str,
        times: List[datetime],
        type: str = "close",
        interpolate_value: Optional[float] = None,
        return_type: ReturnType = ReturnType.LIST,
        return_timestamp: bool = False,
    ):

        with Session(self._conn) as sess:
            s_table = self._symbol_to_prices[symbol]
            (pre_start_at,) = (
                sess.query(func.max(s_table.time)).where(s_table.time <= times[0]).one()
            )

        with Session(self._conn) as sess:
            s_table = self._symbol_to_prices[symbol]

            res = [
                (timestamp(t) if return_timestamp else t, p)
                for t, p in sess.query(
                    s_table.time,
                    getattr(s_table, type),
                )
                .where(s_table.time.in_([pre_start_at] + times))
                .order_by(s_table.time.asc())
            ]

        if datetime is None and interpolate_value is None:
            return res

        index = 0 if pre_start_at == times[0] else 1
        if return_type == ReturnType.LIST:
            populated = []
            for t_ in times:
                t = t_ if not return_timestamp else timestamp(t_)

                if index >= len(res):
                    populated.append((t, res[-1][1]))
                elif t < res[index][0]:
                    populated.append((t, interpolate_value))
                elif t == res[index][0]:
                    populated.append(res[index])
                    index += 1
                else:
                    assert False, (
                        f"something's wrong; time {datetime.fromtimestamp(t)} "
                        f"is bigger than {datetime.fromtimestamp(res[index][0])}"
                    )
        elif return_type == ReturnType.DICT:
            populated = {}
            for t_ in times:
                t = t_ if not return_timestamp else timestamp(t_)

                if index >= len(res):
                    populated[t] = res[-1][1]
                elif t < res[index][0]:
                    populated[t] = interpolate_value
                elif t == res[index][0]:
                    populated[t] = res[index][1]
                    index += 1
                else:
                    assert False, (
                        f"something's wrong; time {datetime.fromtimestamp(t)} "
                        f"is bigger than {datetime.fromtimestamp(res[index][0])}"
                    )
        elif return_type == ReturnType.NUMBA_DICT:
            if not return_timestamp:
                self.validator.add_error(
                    "return type is numba; so timestamp must be returned"
                )
                return nDict.empty(key_type=types.float64, value_type=types.float64)
            populated = nDict.empty(key_type=types.float64, value_type=types.float64)
            for t_ in times:
                t = t_ if not return_timestamp else timestamp(t_)

                if index >= len(res):
                    populated[t] = res[-1][1]
                elif t < res[index][0]:
                    populated[t] = interpolate_value
                elif t == res[index][0]:
                    populated[t] = res[index][1]
                    index += 1
                else:
                    assert False, (
                        f"something's wrong; time {datetime.fromtimestamp(t)} "
                        f"is bigger than {datetime.fromtimestamp(res[index][0])}"
                    )
        else:
            raise NotImplementedError("not implemented")
        return populated

    @validate_atomic
    def take_one(
        self,
        *,
        symbol: str,
        end_at: datetime,
        type: str = "close",
        with_time: bool = False,
        precision: int = 1,
    ):
        end_at <<= 0
        result = self._take_last(
            symbol=symbol,
            end_at=end_at,
            type=type,
            with_time=True,
            strict=False,
            count=1,
        )
        if len(result) < 1:
            self.validator.add_error(
                f"cannot get price for symbol {symbol} at {end_at}"
            )
            return None
        if abs(end_at - result[-1][0]) >= timedelta(minutes=precision):
            self.validator.add_error(
                f"cannot get price for symbol {symbol} at {end_at} with "
                f"precision of {precision} minutes. "
                f"Most recent data obtained at {result[0][0]}"
            )
        return result[-1][1] if not with_time else result

    @validate_atomic
    def percent_change(
        self,
        *,
        symbol: str,
        start_at: datetime,
        end_at: datetime,
        count: int = 1,
        strict: bool = True,
    ):
        start_at <<= 0
        end_at <<= 0
        # TODO: set with time to False to speed this up; we want time for now to debug
        start_prices = self._take_last(
            symbol=symbol, count=count, end_at=start_at, with_time=True, strict=strict
        )
        end_prices = self._take_last(
            symbol=symbol, count=count, end_at=end_at, with_time=True, strict=strict
        )
        start_prices = list(map(itemgetter(1), start_prices))
        end_prices = list(map(itemgetter(1), end_prices))
        if strict and (len(start_prices) != count or len(end_prices) != count):
            self.validator.add_error(f"cannot get {count} prices for symbol {symbol}")
            return float("nan")
        return (
            (average(end_prices) - average(start_prices)) / average(start_prices) * 100
        )

    @validate_atomic
    def max(
        self, *, symbol: str, start_at: datetime, end_at: datetime, type: str = "close"
    ):
        return self._func(
            symbol=symbol,
            start_at=start_at,
            end_at=end_at,
            type=type,
            f=func.max,
            caller_name="max",
        )

    @validate_atomic
    def min(
        self, *, symbol: str, start_at: datetime, end_at: datetime, type: str = "close"
    ):
        return self._func(
            symbol=symbol,
            start_at=start_at,
            end_at=end_at,
            type=type,
            f=func.min,
            caller_name="min",
        )

    def _func(
        self,
        *,
        symbol: str,
        start_at: datetime,
        end_at: datetime,
        type: str,
        f: Callable,
        caller_name: str,
    ):
        if not isinstance(start_at, datetime):
            self.validator.add_error(f"start_at is not a valid datetime but {start_at}")
            return None, None

        if not isinstance(end_at, datetime):
            self.validator.add_error(f"end_at is not a valid datetime but {end_at}")
            return None, None

        start_at <<= 0
        end_at <<= 0
        with Session(self._conn) as sess:
            res = (
                sess.query(
                    self._symbol_to_prices[symbol].time,
                    f(getattr(self._symbol_to_prices[symbol], type)),
                )
                .where(self._symbol_to_prices[symbol].time >= start_at)
                .where(self._symbol_to_prices[symbol].time <= end_at)
                .one()
            )
            if res[0] is None or res[1] is None:
                self.validator.add_error(
                    f"cannot get any data points within the given time "
                    f"frame from {start_at} to {end_at}",
                    caller_name=caller_name,
                )
            return res

    @validate_atomic
    def missing_items(self, *, symbol: str):
        with Session(conn) as sess:
            res = sess.query(MissingPrice).where(MissingPrice.symbol == symbol)
            return res.all()

    @validate_atomic
    def take_latest(self, symbol: str):
        time, price = self._quote_price_api(symbol)
        return time, price


class SymbolPlugin(APIPlugin):
    @validate_atomic
    def get(self, name: str):
        with Session(self._conn) as sess:
            res = sess.query(Symbol.name).where(Symbol.name == name).one()
        if not res:
            return
        return res[0]

    @validate_atomic
    def items(self, position_ids: Optional[List[int]] = None):
        with Session(self._conn) as sess:
            if not position_ids:
                symbols = sess.query(Symbol.name).all()
            else:
                symbols = (
                    sess.query(Position.symbol)
                    .where(Position.id.in_(position_ids))
                    .all()
                )
        return list(set(map(itemgetter(0), symbols)))

    @validate_atomic
    def like(self, pattern: Optional[str] = None):
        with Session(self._conn) as sess:
            symbols = sess.query(Symbol.name)
            if pattern is not None:
                symbols = symbols.where(Symbol.name.like(pattern))
            return list(map(itemgetter(0), symbols))


class AccumulationPlugin(APIPlugin):
    def __init__(self, *args, **kwargs):
        super(AccumulationPlugin, self).__init__(*args, **kwargs)

        def factory(symbol):
            with warnings.catch_warnings():
                # ignore sql warning for redeclaring class
                warnings.simplefilter("ignore")
                return type(
                    symbol,
                    (Price,),
                    {"__table_args__": {"extend_existing": True}},
                    table=True,
                )

        self._symbol_to_prices = defaultkeydict(factory)
        SQLModel.metadata.create_all(self._conn)

    def _take_every(
        self,
        accumulate_fn: Callable,
        positions: Optional[
            Union[PositionTuple, List[PositionTuple], Dict, ZipPositions]
        ] = None,
        *,
        interval_length: int,
        start_at: datetime,
        end_at: datetime,
        # null_value: float = float('nan'),
        interpolate_value: float = float("nan"),
    ):
        start_at <<= 0
        end_at <<= 0

        if interval_length <= 0:
            self.validator.add_error("interval_length cannot be less than/equal to 0")
            return

        if not isinstance(positions, ZipPositions):
            self._logger.debug(
                "If this is called for multiple time spans, "
                "for faster performance, please retrieve and zip all positions"
            )
        if positions is None:
            positions = self.api.position.items(
                return_timestamp=True, return_tags=False
            )
        elif isinstance(positions, PositionTuple):
            positions = [positions]
        elif isinstance(positions, Dict):
            positions.update({"return_timestamp": True})
            positions = self.api.position.items(**positions, return_tags=False)
        elif isinstance(positions, list):
            assert (not positions) or isinstance(
                positions[0], PositionTuple
            ), f"position is a list but item is not PositionTuple, got {type(positions[0])}"  # noqa: E501

        elif not isinstance(positions, ZipPositions):
            assert False, f"unsupported type for positions, got {type(positions)}"

        # positions at this point can either be: List[PositionTuple] OR ZipPositions
        if not isinstance(positions, ZipPositions):
            with timeit(f"{type(self)} - zip_positions", self._logger.debug):
                positions = zip_positions(positions)

        assert isinstance(
            positions, ZipPositions
        ), "positions is expected to be ZipPositions at this point"
        assert positions.open_ats is not None, "open_ats cannot be None"
        assert positions.close_ats is not None, "close_ats cannot be None"
        assert positions.open_prices is not None, "open_prices cannot be None"
        assert positions.close_prices is not None, "close_prices cannot be None"
        assert positions.quantitys is not None, "quantitys cannot be None"
        assert positions.symbols is not None, "symbols cannot be None"
        assert positions.symbol_hashes is not None, "symbol_hashes cannot be None"

        symbols = set(positions.symbols)
        times = list(trange(start_at, end_at, interval_length, end_inclusive=True))

        with timeit(f"{type(self)} - get prices", self._logger.debug):
            prices = nDict.empty(
                key_type=typeof(0),
                value_type=typeof(
                    nDict.empty(key_type=typeof(0.0), value_type=typeof(0.0))
                ),
            )

            prices.update(
                {
                    shash: self.api.price.take_at(
                        symbol=symbol,
                        times=times,
                        interpolate_value=interpolate_value,
                        return_timestamp=True,
                        return_type=ReturnType.NUMBA_DICT,
                    )
                    for symbol, shash in zip(symbols, positions.symbol_hashes)
                }
            )

        times = np.array([timestamp(t) for t in times], dtype=np.float64)

        with timeit(f"{type(self)} - accumulate", self._logger.debug):
            signal = accumulate_fn(
                times,
                positions.open_ats,
                positions.close_ats,
                positions.open_prices,
                positions.close_prices,
                positions.quantitys,
                positions.symbol_hashes,
                prices,
            )

        with timeit(f"{type(self)} - filter", self._logger.debug):
            res = list(
                map(
                    lambda item: (
                        datetime.fromtimestamp(item[0])
                        if item[0] != float("inf")
                        else datetime.max,
                        item[1],
                    ),
                    sorted(
                        filter(lambda item: not isnan(item[1]), signal.items()),
                        key=lambda item: item[0],
                    ),
                )
            )
        return res


class ProfitPlugin(AccumulationPlugin):
    @validate_atomic
    def take_every(
        self,
        positions: Optional[Union[PositionTuple, List[PositionTuple], Dict]] = None,
        *,
        interval_length: int,
        start_at: datetime,
        end_at: datetime,
    ):
        return self._take_every(
            accumulate_profits,
            positions,
            interval_length=interval_length,
            start_at=start_at,
            end_at=end_at,
        )

    @validate_atomic
    def take_one(
        self,
        positions: Optional[Union[PositionTuple, List[PositionTuple], Dict]] = None,
        *,
        end_at: datetime,
        precision: int = 5,
    ):
        profits = self.take_every(
            positions=positions,
            interval_length=1,
            start_at=(end_at - timedelta(minutes=precision)),
            end_at=end_at,
        )
        for profit in reversed(profits):
            if not isnan(profit[1]):
                return profit
        self.validator.add_error(
            f"cannot get non-nan value from possible values, profits: {profits}"
        )
        return None, 888


class InvestedPlugin(AccumulationPlugin):
    @validate_atomic
    def take_every(
        self,
        positions: Optional[Union[PositionTuple, List[PositionTuple], Dict]] = None,
        *,
        interval_length: int,
        start_at: datetime,
        end_at: datetime,
    ):
        return self._take_every(
            accumulate_investeds,
            positions,
            interval_length=interval_length,
            start_at=start_at,
            end_at=end_at,
        )

    @validate_atomic
    def take_one(
        self,
        positions: Optional[Union[PositionTuple, List[PositionTuple], Dict]] = None,
        *,
        end_at: datetime,
        precision: int = 5,
    ):
        investeds = self.take_every(
            positions=positions,
            interval_length=1,
            start_at=(end_at - timedelta(minutes=precision)),
            end_at=end_at,
        )
        for invested in reversed(investeds):
            if not isnan(invested[1]):
                return invested
        self.validator.add_error(
            f"cannot get non-nan value from possible values, investeds: {investeds}"
        )
        return None, None


class PositionPlugin(APIPlugin):
    def __init__(self, can_open, *args, **kwargs):
        super(PositionPlugin, self).__init__(*args, **kwargs)
        self.can_open = can_open

    @validate_atomic
    def get(self, id_: int) -> Position:
        with Session(self._conn) as sess:
            try:
                res = sess.query(Position).where(Position.id == id_).one()
            except sqlalchemy.exc.NoResultFound:
                return None
            return res

    @validate_atomic
    def update(
        self,
        id_: int,
        *,
        symbol: Optional[str] = None,
        position: Optional[str] = None,
        status: Optional[str] = None,
        quantity: Optional[int] = None,
        open_price: Optional[float] = None,
        close_price: Optional[float] = None,
        open_at: Optional[datetime] = None,
        close_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        tag: Optional[str] = None,
    ):
        stmt = update(Position).where(Position.id == bindparam("id_"))

        value = {"id_": id_}
        if symbol is not None:
            stmt = stmt.values(symbol=bindparam("symbol"))
            value["symbol"] = symbol

        if position is not None:
            stmt = stmt.values(position=bindparam("position"))
            value["position"] = position

        if status is not None:
            stmt = stmt.values(status=bindparam("status"))
            value["status"] = status

        if quantity is not None:
            stmt = stmt.values(quantity=bindparam("quantity"))
            value["quantity"] = quantity

        if open_price is not None:
            stmt = stmt.values(open_price=bindparam("open_price"))
            value["open_price"] = open_price

        if close_price is not None:
            stmt = stmt.values(close_price=bindparam("close_price"))
            value["close_price"] = close_price

        if open_at is not None:
            stmt = stmt.values(open_at=bindparam("open_at"))
            value["open_at"] = open_at

        if close_at is not None:
            stmt = stmt.values(close_at=bindparam("close_at"))
            value["close_at"] = close_at

        if updated_at is not None:
            stmt = stmt.values(updated_at=bindparam("updated_at"))
            value["updated_at"] = updated_at

        if tag is not None:
            stmt = stmt.values(tag=bindparam("tag"))
            value["tag"] = tag

        with Session(self._conn) as sess:
            sess.execute(stmt, [value])
            sess.commit()

    @validate_atomic
    def open(
        self,
        *,
        symbol: str,
        quantity: int,
        position: float,
        price: float,
        stop_price: float,
        cooldown_period: Optional[int] = None,
        tags: Optional[Dict] = None,
        time: Optional[datetime] = None,
    ):
        """
        This method opens an position.

        :param symbol: the symbol to open position for
        :param quantity: the quantity to open position for.
        """
        if price is None or price == 0:
            return False

        if not self.can_open():
            return False

        tags = tags or {}

        time = time or self._timer.now()
        if cooldown_period and self.has(
            symbol=symbol,
            position=position,
            status="open",
            open_at_or_after=time << cooldown_period,
        ):
            return False

        with Session(self._conn) as sess:
            pos = Position(
                symbol=symbol,
                status="submit_open",
                submit_open_price=price,
                submit_open_at=time,
                quantity=quantity,
                position=position,
                updated_at=time,
                stop_open_price=stop_price,
            )
            sess.add(pos)
            sess.commit()
            sess.refresh(pos)
            for k, v in tags.items():
                if isinstance(v, (int, float)) or (isinstance(v, str) and v.isfloat()):
                    sess.add(NumberTag(name=k, value=v, position_id=pos.id))
                elif isinstance(v, bool) or (
                    isinstance(v, str) and v in ("true", "True", "false", "False")
                ):
                    sess.add(BoolTag(name=k, value=v, position_id=pos.id))
                elif isinstance(v, str):
                    sess.add(StrTag(name=k, value=v, position_id=pos.id))
                else:
                    self.validator.add_error(
                        f"invalid tag {key}: value {val} is not a valid type"
                    )
                    return False

            sess.commit()
            return True

    @validate_atomic
    def close(
        self,
        id: int,
        *,
        price: float,
        stop_price: float,
        time: Optional[datetime] = None,
        quantity: Optional[int] = None,
    ):
        """
        This method closes an position.

        :param id: the id of the openede position
        """

        time = time or self._timer.now() >> 0

        stmt = (
            update(Position)
            .where(Position.id == id)
            .values(submit_close_price=price)
            .values(submit_close_at=time)
            .values(status="submit_close")
            .values(stop_close_price=stop_price)
        )

        if quantity is not None:
            stmt = stmt.values(quantity=quantity)

        with Session(self._conn) as sess:
            closed_pos = sess.query(Position).where(Position.id == id).one()

        with Session(self._conn) as sess:
            sess.execute(stmt)
            sess.commit()

        if quantity is None or closed_pos.quantity == quantity:
            return

        # open residue
        pos = Position(
            symbol=closed_pos.symbol,
            status="open",
            submit_open_price=closed_pos.submit_open_price,
            submit_open_at=closed_pos.submit_open_at,
            open_price=closed_pos.open_price,
            open_at=closed_pos.open_at,
            quantity=closed_pos.quantity - quantity,
            position=closed_pos.position,
            updated_at=time,
            stop_open_price=closed_pos.stop_open_price,
        )

        with Session(self._conn) as sess:
            sess.add(pos)
            sess.commit()
            sess.refresh(pos)
            for cls in [NumberTag, StrTag, BoolTag]:
                for tag in sess.query(cls).where(cls.position_id == closed_pos.id):
                    sess.add(cls(name=tag.name, value=tag.value, position_id=pos.id))
            sess.commit()

    @validate_atomic
    def count(
        self,
        request: Optional[PositionSelectRequest] = None,
        *,
        symbol: Optional[Union[str, List[str]]] = None,
        status: Optional[Union[str, List[str]]] = None,
        id: Optional[Union[int, List[int]]] = None,
        position: Optional[Union[str, List[str]]] = None,
        open_at_or_before: Optional[datetime] = None,
        open_at_or_after: Optional[datetime] = None,
        close_at_or_before: Optional[datetime] = None,
        close_at_or_after: Optional[datetime] = None,
        pagination_args: Optional[Dict] = None,
    ) -> int:
        if request and any(
            [
                symbol,
                status,
                id,
                position,
                open_at_or_before,
                open_at_or_after,
                close_at_or_before,
                close_at_or_after,
            ]
        ):
            self.validator.add_error(
                "this function takes either a request object or "
                "specific parameters, not both"
            )
            return None

        if request:
            return self._count_by_request(request)

        status = status or ["open", "close"]

        with Session(self._conn) as sess:
            q = sess.query(func.count(Position.id))
            if symbol is not None:
                q = q.where(Position.symbol.in_(symbol))
            if id is not None:
                q = q.where(Position.id.in_(id))
            if status is not None:
                q = q.where(Position.status.in_(status))
            if position is not None:
                q = q.where(Position.position.in_(position))
            if open_at_or_before is not None:
                q = q.where(Position.open_at <= open_at_or_before)
            if open_at_or_after is not None:
                q = q.where(Position.open_at >= open_at_or_after)
            if close_at_or_before is not None:
                q = q.where(Position.close_at <= close_at_or_before)
            if close_at_or_after is not None:
                q = q.where(Position.close_at >= close_at_after)
            return q.scalar()

    def _count_by_request(self, req):
        with Session(self._conn) as sess:
            stmt = sess.query(func.count(Position.id))

            if req.symbol is not None:
                stmt = stmt.where(Position.symbol.like(req.symbol + "%"))

            if req.status is not None:
                stmt = stmt.where(Position.status.in_(req.status))

            if req.position is not None:
                stmt = stmt.where(Position.position.in_(req.position))

            if req.quantity is not None:
                stmt = stmt.where(
                    getattr(Position.quantity, req.quantity.operator)(
                        req.quantity.operand
                    )
                )

            if req.open_price is not None:
                stmt = stmt.where(
                    getattr(Position.open_price, req.open_price.operator)(
                        req.open_price.operand
                    )
                )

            if req.open_at is not None:
                stmt = stmt.where(
                    getattr(Position.open_at, req.open_at.operator)(req.open_at.operand)
                )

            if req.tags is not None:
                filter_clause = to_sqlalchemy_query(req.tags)
                stmt = stmt.where(filter_clause)

            return stmt.scalar()

    @validate_atomic
    def items(
        self,
        *,
        request: Optional[PositionSelectRequest] = None,
        symbol: Optional[Union[str, List[str]]] = None,
        status: Optional[Union[str, List[str]]] = None,
        id: Optional[Union[int, List[int]]] = None,
        position: Optional[Union[str, List[str]]] = None,
        open_at_or_before: Optional[datetime] = None,
        open_at_or_after: Optional[datetime] = None,
        close_at_or_before: Optional[datetime] = None,
        close_at_or_after: Optional[datetime] = None,
        pagination_args: Optional[Dict] = None,
        fields: List[str] = list(Position.__fields__.keys()),
        return_timestamp: bool = False,
        return_tags: bool = True,
    ) -> List[PositionTuple]:
        if request and any(
            [
                symbol,
                # status,
                id,
                position,
                open_at_or_before,
                open_at_or_after,
                close_at_or_before,
                close_at_or_after,
            ]
        ):
            self.validator.add_error(
                "this function takes either a request object or "
                "specific parameters, not both"
            )
            return None

        if request:
            return self._items_by_request(request, pagination_args=pagination_args)

        status = status or ["open", "close"]

        if symbol and not isinstance(symbol, List):
            symbol = [symbol]
        if status and not isinstance(status, List):
            status = [status]
        if id and not isinstance(id, List):
            id = [id]
        if position and not isinstance(position, List):
            position = [position]

        if "id" not in fields:
            fields = ["id"] + fields

        fields = [getattr(Position, f) for f in fields]
        with Session(self._conn) as sess:
            q = sess.query(*fields)
            if symbol is not None:
                q = q.where(Position.symbol.in_(symbol))
            if id is not None:
                q = q.where(Position.id.in_(id))
            if status is not None:
                q = q.where(Position.status.in_(status))
            if position is not None:
                q = q.where(Position.position.in_(position))
            if open_at_or_before is not None:
                q = q.where(Position.open_at <= open_at_or_before)
            if open_at_or_after is not None:
                q = q.where(Position.open_at >= open_at_or_after)
            if close_at_or_before is not None:
                q = q.where(Position.close_at <= close_at_or_before)
            if close_at_or_after is not None:
                q = q.where(Position.close_at >= close_at_after)

            q = q.order_by(Position.id.desc())

            if pagination_args is not None:
                page, limit, last_id = (
                    pagination_args["page"],
                    pagination_args["limit"],
                    pagination_args["last_id"],
                )
                if last_id is not None:
                    q = q.where(Position.id <= last_id)
                row_number_column = (
                    func.row_number().over(order_by=Position.id.desc()).label("rnum")
                )
                q = (
                    q.add_column(row_number_column)
                    .from_self()
                    .where(
                        and_(
                            row_number_column - 1 >= page * limit,
                            row_number_column - 1 < (page + 1) * limit,
                        )
                    )
                )
                results = {pos[0]: PositionTuple(*pos, tags={}) for *pos, _ in q}
            else:
                results = {pos[0]: PositionTuple(*pos, tags={}) for pos in q}

            if return_timestamp:
                results = {k: v.datetime_to_timestamp() for k, v in results.items()}

            if return_tags:
                ids = results.keys()
                for pid, name, val in list(
                    itertools.chain.from_iterable(
                        sess.query(Tag.position_id, Tag.name, Tag.value).where(
                            Tag.position_id.in_(ids)
                        )
                        for Tag in [BoolTag, NumberTag, StrTag]
                    )
                ):
                    results[pid].tags.update({name: val})

            return list(results.values())

    def _items_by_request(
        self, req: PositionSelectRequest, pagination_args: Optional[Dict] = None
    ):
        with Session(self._conn) as sess:
            stmt = sess.query(Position)
            if req.symbol is not None:
                stmt = stmt.where(Position.symbol.like(req.symbol + "%"))

            if req.status is not None:
                stmt = stmt.where(Position.status.in_(req.status))

            if req.position is not None:
                stmt = stmt.where(Position.position.in_(req.position))

            if req.quantity is not None:
                stmt = stmt.where(
                    getattr(Position.quantity, req.quantity.operator)(
                        req.quantity.operand
                    )
                )

            if req.open_price is not None:
                stmt = stmt.where(
                    getattr(Position.open_price, req.open_price.operator)(
                        req.open_price.operand
                    )
                )

            if req.open_at is not None:
                stmt = stmt.where(
                    getattr(Position.open_at, req.open_at.operator)(req.open_at.operand)
                )

            if req.close_at is not None:
                stmt = stmt.where(
                    getattr(Position.close_at, req.close_at.operator)(
                        req.close_at.operand
                    )
                )

            if req.tags is not None:
                filter_clause = to_sqlalchemy_query(req.tags)
                stmt = stmt.where(filter_clause)

            if pagination_args is not None:
                page, limit, last_id = (
                    pagination_args["page"],
                    pagination_args["limit"],
                    pagination_args["last_id"],
                )
                if last_id is not None:
                    stmt = stmt.where(Position.id <= last_id)
                row_number_column = (
                    func.row_number().over(order_by=Position.id.desc()).label("rnum")
                )
                stmt = (
                    stmt.add_column(row_number_column)
                    .from_self()
                    .where(
                        and_(
                            row_number_column - 1 >= page * limit,
                            row_number_column - 1 < (page + 1) * limit,
                        )
                    )
                )

            if pagination_args:
                results = {
                    pos.id: PositionTuple(**pos.dict(), tags={}) for pos, _ in stmt
                }
            else:
                results = {pos.id: PositionTuple(**pos.dict(), tags={}) for pos in stmt}

            ids = results.keys()
            for pid, name, val in list(
                itertools.chain.from_iterable(
                    sess.query(Tag.position_id, Tag.name, Tag.value).where(
                        Tag.position_id.in_(ids)
                    )
                    for Tag in [BoolTag, NumberTag, StrTag]
                )
            ):
                results[pid].tags.update({name: val})
            return list(results.values())

    @validate_atomic
    def has(
        self,
        request: Optional[PositionSelectRequest] = None,
        *,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        id: Optional[List[int]] = None,
        position: Optional[str] = None,
        open_at_or_before: Optional[datetime] = None,
        open_at_or_after: Optional[datetime] = None,
        close_at_or_before: Optional[datetime] = None,
        close_at_or_after: Optional[datetime] = None,
    ):
        return not not self.items(
            request=request,
            status=status,
            id=id,
            position=position,
            open_at_or_before=open_at_or_before,
            open_at_or_after=open_at_or_after,
            close_at_or_before=close_at_or_before,
            close_at_or_after=close_at_or_after,
        )

    @validate_atomic
    def get_prices_from_open_until_close(
        self,
        num_points: int,
        positions: Optional[Union[PositionTuple, List[PositionTuple], Dict]] = None,
        *,
        min_extra_duration: int,
        extra_duration_percent: int,
    ):
        """
        This api gets the prices through time of the given positions from open to
        close. Users need to provide:
        1) `min_extra_duration` - min extra duration in minutes
        2) `extra_duration_percent` - decimal representing extra duration percentage
        to get the prices before open and after close.
        """
        if not positions:
            position_ids = None
        elif positions and isinstance(positions, PositionTuple):
            position_ids = [positions.id]
        elif positions and isinstance(positions, list):
            assert isinstance(positions[0], PositionTuple)
            position_ids = [p.id for p in positions]
        elif isinstance(positions, Dict):
            position_ids = [positions["id"]]
        else:
            assert False, f"positions type is unspported, got {type(positions)}"

        symbols = self.api.symbol.items(position_ids=position_ids)
        now = self._timer.now(minute_only=True)

        results = {}
        for symbol in symbols:
            positions = self.items(symbol=symbol, id=position_ids)
            times, prices = self.api.price.take(symbol=symbol)
            for pos in positions:
                results[pos.id] = self._get_prices(
                    prices=prices,
                    times=times,
                    pos=pos,
                    now=now,
                    num_points=num_points,
                    extra_duration_percent=extra_duration_percent,
                    min_extra_duration=min_extra_duration,
                )
        return results

    def _get_prices(
        self,
        prices: List[float],
        times: List[float],
        pos: Position,
        now: datetime,
        num_points: int,
        extra_duration_percent: Optional[float] = None,
        min_extra_duration: Optional[float] = None,
    ) -> Signal:
        start_at = pos.open_at.replace(second=0, microsecond=0)
        end_at = (
            now
            if pos.close_at == datetime.max
            else pos.close_at.replace(second=0, microsecond=0)
        )
        duration = end_at - pos.open_at
        extra_duration = max(
            timedelta(minutes=min_extra_duration), (duration * extra_duration_percent)
        )
        start_index = bisect_left(times, start_at)
        end_index = bisect_left(times, end_at)

        pre_at = (start_at - extra_duration).replace(second=0, microsecond=0)
        post_at = (end_at + extra_duration).replace(second=0, microsecond=0)

        pre_index = bisect_left(times, pre_at)
        post_index = bisect_left(times, post_at)

        if start_index >= len(times):
            return Signal([], [], [])

        # NOTE disable the following because there might be missing prices
        # assert (
        #     abs(times[start_index] - start_at) <= timedelta(minutes=1)
        # ), f'{times[start_index]} does not match {start_at}'

        postprocess = lambda s, e, n: downsample(
            list(map(Datum._make, zip(times[s:e], prices[s:e]))), n
        )
        pre = postprocess(
            pre_index, start_index + 1, num_points * extra_duration_percent
        )
        actual = postprocess(start_index, end_index + 1, num_points)
        post = postprocess(end_index, post_index, num_points * extra_duration_percent)

        # modify price at open time to be precise
        actual[0] = Datum(pos.open_at, pos.open_price)
        if pre:
            pre[-1] = Datum(pos.open_at, pos.open_price)

        # modify price at close time to be precise
        if pos.close_at == end_at and len(actual) == 1:
            actual.append(Datum(pos.close_at, pos.close_price))
        elif pos.close_at == end_at:
            actual[-1] = Datum(pos.close_at, pos.close_price)
        if post:
            post[0] = Datum(pos.close_at, pos.close_price)

        return Signal(pre, actual, post)


class ExchangeAPI:
    """
    This ExchangeAPI object expose all the neccessary APIs for users
    to interact with the exchange.

    :param database_addr: the address of the database
    """

    def __init__(
        self,
        db_conn: Union[str, sqlalchemy.engine.base.Engine],
        *,
        validator: Validator = Validator(),
        can_open: Callable = lambda: True,
        get_version: Callable = lambda: 1,
        is_updating: Callable = lambda: True,
        timer: Timer = Timer(),
        logger: Optional[Logger] = None,
        source: str = "webull",
    ):
        self.validator = validator
        self.get_version = get_version
        self.is_updating = is_updating
        self._conn = create_engine(db_conn) if isinstance(db_conn, str) else db_conn

        self._timer = timer
        self._logger = logger or Logger(name="api", timer=self._timer, level="INFO")
        self._apis = {
            "price": PricePlugin(
                api=self,
                conn=self._conn,
                timer=self._timer,
                logger=self._logger,
                validator=validator,
                get_version=get_version,
                is_updating=is_updating,
                source=source,
            ),
            "position": PositionPlugin(
                api=self,
                conn=self._conn,
                timer=self._timer,
                logger=self._logger,
                validator=validator,
                can_open=can_open,
                get_version=get_version,
                is_updating=is_updating,
            ),
            "symbol": SymbolPlugin(
                api=self,
                conn=self._conn,
                timer=self._timer,
                logger=self._logger,
                validator=validator,
                get_version=get_version,
                is_updating=is_updating,
            ),
            "profit": ProfitPlugin(
                api=self,
                conn=self._conn,
                timer=self._timer,
                logger=self._logger,
                validator=validator,
                get_version=get_version,
                is_updating=is_updating,
            ),
            "invested": InvestedPlugin(
                api=self,
                conn=self._conn,
                timer=self._timer,
                logger=self._logger,
                validator=validator,
                get_version=get_version,
                is_updating=is_updating,
            ),
        }
        try:
            SQLModel.metadata.create_all(self._conn)
        except sqlalchemy.exc.OperationalError:
            pass
        self.now = self._timer.now

    @property
    def price(self):
        """
        This returns the ``PricePlugin`` API which allows users to
        get information of prices.

        :returns: a ``PricePlugin`` object
        """
        return self._apis["price"]

    @property
    def position(self):
        """
        This returns the ``PositionPlugin`` API which allows users to
        get information of positions, or open/close given position(s).

        :returns: a ``PositionPlugin`` object
        """
        return self._apis["position"]

    @property
    def symbol(self):
        """
        This returns the ``SymbolPlugin`` API which allows users to
        get information of symbols.

        :returns: a ``SymbolPlugin`` object
        """
        return self._apis["symbol"]

    @property
    def profit(self):
        """
        This returns the ``ProfitPlugin`` API which allows users to
        get information of profit.

        :returns: a ``ProfitPlugin`` object
        """
        return self._apis["profit"]

    @property
    def invested(self):
        """
        This returns the ``InvestedPlugin`` API which allows users to
        get information of invested.

        :returns: a ``InvestedPlugin`` object
        """
        return self._apis["invested"]

    def __iter__(self):
        yield from self._apis

    def items(self):
        """
        Similar to python dict ``items`` method, this return a
        sequence of all API plugins, along with thei key names as tuples

        :returns: a list of name and API items tuples
        """
        return self._apis.items()

    def keys(self):
        """
        Similar to python dict ``keys`` method, this return a
        sequence of all API plugin key names

        :returns: a list of API names
        """
        return self._apis.keys()

    def values(self):
        """
        Similar to python dict ``values`` method, this return a
        sequence of all API plugins

        :returns: a list of API items
        """
        return self._apis.values()
