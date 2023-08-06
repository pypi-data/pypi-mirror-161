import uuid
import re
from collections import namedtuple
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from datetime import time as datetime_time
from sqlmodel import Field, SQLModel, Column, DateTime, Integer, ForeignKey
from forbiddenfruit import curse
from pydantic import BaseModel, validator
import sqlalchemy
from sqlalchemy import and_

from greap.cache import timestamp


OPEN_HOURS_DURATION_COUNT = 390

NEXT_DAY_COUNT = 1050

MAX_COUNT = 800

UNCERTAIN_WINDOW = 20


class Symbol(SQLModel, table=True):
    name: str = Field(primary_key=True)
    start_at: datetime
    end_at: datetime


# Note, table=True not set because this is only a base class/table
class Price(SQLModel):
    time: datetime = Field(sa_column=Column(DateTime(timezone=False), primary_key=True))
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float


class Profit(SQLModel, table=True):
    position_id: int = Field(
        sa_column=Column(Integer, ForeignKey("position.id"), primary_key=True)
    )
    time: datetime = Field(sa_column=Column(DateTime(timezone=False), primary_key=True))
    profit: float
    open_price: float
    curr_price: float


class MissingPrice(SQLModel, table=True):
    time: datetime = Field(sa_column=Column(DateTime(timezone=False), primary_key=True))
    symbol: str = Field(primary_key=True)


class Position(SQLModel, table=True):
    id: int = Field(primary_key=True)
    symbol: str
    position: str
    status: str
    quantity: int
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    open_at: datetime = Field(
        default=datetime.max, sa_column=Column(DateTime(timezone=False))
    )
    close_at: datetime = Field(
        default=datetime.max, sa_column=Column(DateTime(timezone=False))
    )
    updated_at: datetime

    # connector related
    stop_open_price: float
    stop_close_price: Optional[float] = None
    submit_close_price: Optional[float] = None
    submit_open_price: float
    submit_open_at: datetime
    submit_close_at: datetime = Field(
        default=datetime.max, sa_column=Column(DateTime(timezone=False))
    )


class PositionMetadata(SQLModel, table=True):
    position_id: int = Field(
        sa_column=Column(Integer, ForeignKey("position.id"), primary_key=True)
    )
    open_order_id: str
    close_order_id: Optional[str] = None

    submit_open_at: datetime
    open_at: Optional[datetime] = None
    submit_close_at: Optional[datetime] = None
    close_at: Optional[datetime] = None


# accessing attribute of SQLModel is slow, use tuple instead
_PositionTuple = namedtuple(
    "PositionTuple", list(Position.__fields__.keys()) + ["tags"]
)


class PositionTuple(_PositionTuple):
    def datetime_to_timestamp(self):
        repl = {}
        for field in self._fields:
            val = getattr(self, field)
            if isinstance(val, datetime):
                try:
                    repl[field] = timestamp(val)
                except ValueError:
                    repl[field] = float("inf")
        return self._replace(**repl)


ZipPositions = namedtuple(
    "ZipPositions",
    [
        "ids",
        "symbols",
        "positions",
        "statuss",
        "quantitys",
        "open_ats",
        "close_ats",
        "open_prices",
        "close_prices",
        "updated_ats",
        "symbol_hashes",
        "tags",
    ],
)


class StrTag(SQLModel, table=True):
    position_id: int = Field(
        sa_column=Column(Integer, ForeignKey("position.id"), primary_key=True)
    )
    name: str = Field(primary_key=True)
    value: str


class NumberTag(SQLModel, table=True):
    position_id: int = Field(
        sa_column=Column(Integer, ForeignKey("position.id"), primary_key=True)
    )
    name: str = Field(primary_key=True)
    value: float


class BoolTag(SQLModel, table=True):
    position_id: int = Field(
        sa_column=Column(Integer, ForeignKey("position.id"), primary_key=True)
    )
    name: str = Field(primary_key=True)
    value: bool


def weekend_to_next_monday(self):
    if self.weekday() == 5:
        return self + timedelta(days=2)
    if self.weekday() == 6:
        return self + timedelta(days=1)
    return self


def weekend_to_prev_friday(self):
    if self.weekday() == 5:
        return self - timedelta(days=1)
    elif self.weekday() == 6:
        return self - timedelta(days=2)
    return self


def increment(t: datetime, minutes=1):
    t = t.replace(second=0, microsecond=0)
    days, minutes = (
        minutes // OPEN_HOURS_DURATION_COUNT,
        minutes % OPEN_HOURS_DURATION_COUNT,
    )
    weeks, days = days // 5, days % 5

    # if it's before 09:31, make it 09:31
    if t.time() > datetime_time(16, 0):
        t += timedelta(days=1)
        t = t.replace(hour=9, minute=31)
    elif t.time() < datetime_time(9, 31):
        t = t.replace(hour=9, minute=31)

    new_time = t + timedelta(minutes=minutes)
    if new_time > datetime(t.year, t.month, t.day, 16, 0, 0, 0):
        new_time += timedelta(minutes=NEXT_DAY_COUNT)

    new_time = weekend_to_next_monday(new_time)
    if (4 - new_time.weekday()) - days < 0:
        new_time += timedelta(days=2)
    new_time += timedelta(days=days)
    return new_time + timedelta(weeks=weeks)


def decrement(time: datetime, minutes=1):
    time = time.replace(second=0, microsecond=0)
    days, minutes = (
        minutes // OPEN_HOURS_DURATION_COUNT,
        minutes % OPEN_HOURS_DURATION_COUNT,
    )
    weeks, days = days // 5, days % 5
    # if it's after 16:00, make it 16:00
    if time.time() > datetime_time(16, 0):
        time = time.replace(hour=16, minute=0)
    elif time.time() < datetime_time(9, 31):
        time -= timedelta(days=1)
        time = time.replace(hour=16, minute=0)

    new_time = time - timedelta(minutes=minutes)
    if new_time < datetime(time.year, time.month, time.day, 9, 31, 0, 0):
        new_time -= timedelta(minutes=NEXT_DAY_COUNT)

    new_time = weekend_to_prev_friday(new_time)
    if (new_time.weekday()) - days < 0:
        new_time -= timedelta(days=2)
    new_time -= timedelta(days=days)
    return new_time - timedelta(weeks=weeks)


def lshift(self, minutes: int):
    return decrement(self, minutes)


def rshift(self, minutes: int):
    return increment(self, minutes)


def trange(
    start: datetime,
    stop: datetime,
    step: int,
    end_inclusive: bool = False,
    return_timestamp: bool = False,
):
    assert step > 0, "step needs to be positive"
    last = None
    curr = increment(start, 0)
    while curr < stop:
        yield timestamp(curr) if return_timestamp else curr
        last = curr
        curr = increment(curr, step)
    if end_inclusive and (last is None or last < stop):
        yield timestamp(stop) if return_timestamp else stop


def prev_open_time(self) -> datetime:
    repl = self.replace(hour=9, minute=31, second=0)
    if repl >= self:
        repl = repl - timedelta(days=1)
    return weekend_to_prev_friday(repl)


def prev_close_time(self) -> datetime:
    repl = self.replace(hour=16, minute=1, second=0)
    if repl >= self:
        repl = repl - timedelta(days=1)
    return weekend_to_prev_friday(repl)


def next_open_time(self) -> datetime:
    repl = self.replace(hour=9, minute=31, second=0)
    if repl < self:
        repl = repl + timedelta(days=1)
    return weekend_to_next_monday(repl)


def next_close_time(self) -> datetime:
    repl = self.replace(hour=16, minute=1, second=0)
    if repl < self:
        repl = repl + timedelta(days=1)
    return weekend_to_next_monday(repl)


def is_open(self):
    return (
        datetime_time(hour=9, minute=31)
        <= self.time()
        < datetime_time(hour=16, minute=1)
        and self.weekday() <= 4
    )


def next_day(self, weekday=0, hour=0, minute=0, second=0):
    repl = self.replace(hour=hour, minute=minute, second=second)

    if self.weekday() == weekday:
        return repl if repl >= self else repl + timedelta(days=7)

    num_days = (
        weekday - self.weekday()
        if weekday > self.weekday()
        else weekday - self.weekday() + 6
    )
    return repl + timedelta(days=num_days)


def open_hours_delta(start, end):
    count = 0
    while start < end:
        start >>= 1
        count += 1
    return count


curse(datetime, "__lshift__", lshift)
curse(datetime, "__rshift__", rshift)
curse(datetime, "prev_open_time", prev_open_time)
curse(datetime, "prev_close_time", prev_close_time)
curse(datetime, "next_open_time", next_open_time)
curse(datetime, "next_close_time", next_close_time)
curse(datetime, "is_open", is_open)
curse(datetime, "next_day", next_day)


# Request/Response Models
OP2C = {
    ">=": "__ge__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
}


OP1C = {
    ">": "__gt__",
    "<": "__lt__",
    "=": "__eq__",
}

BOOLOP = {
    "and": "and_",
    "&&": "and_",
    "&": "and_",
    "or": "or_",
    "||": "or_",
    "|": "or_",
}

OPS = {**OP2C, **OP1C, **BOOLOP}

OPPair = namedtuple("OPPair", ["operator", "operand"])

Datum = namedtuple("Datum", ["time", "value"])

Signal = namedtuple("Signal", ["pre", "actual", "post"])


def _make_tag_condition(
    left: Optional[str] = None,
    op: Optional[str] = None,
    right: Optional[str] = None,
    pl: Optional[str] = None,
):
    assert (all(v is not None for v in [left, op, right]) and pl is None) or (
        pl is not None and all(v is None for v in [left, op, right])
    )
    if pl is not None:
        return PlaceholderCondition(pl)
    else:
        return ComparableCondition(left, OPS[op], right)


ComparableCondition = namedtuple("ComparableCondition", ["left", "op", "right"])

PlaceholderCondition = namedtuple("ComparableCondition", ["name"])


class Response(BaseModel):
    type: str
    now: datetime


class _InvestedRequest(BaseModel):
    ids: Optional[str] = None


class InvestedRequest(_InvestedRequest):
    @validator("ids")
    def valid_ids(cls, v: str):
        if v is None:
            return v
        return list(map(int, v.split(",")))


class ProfitItem(BaseModel):
    signal: List[Datum]
    invested: float
    dollar_change: float
    last_updated: datetime


class InvestedResponse(Response):
    d: ProfitItem
    d3: ProfitItem
    w: ProfitItem
    m: ProfitItem
    y: ProfitItem


class _PositionSelectRequest(BaseModel):
    symbol: Optional[str] = None
    status: Optional[str] = None
    position: Optional[str] = None
    quantity: Optional[str] = None
    open_at: Optional[str] = None
    close_at: Optional[str] = None
    open_price: Optional[str] = None
    current_price: Optional[str] = None
    percent_return: Optional[str] = None
    tags: Optional[str] = None
    percent_change: Optional[float] = None
    dollar_change: Optional[float] = None

    page: Optional[int] = None
    limit: Optional[int] = None
    last_id: Optional[int] = None


def compile_query(query):
    def _match_parantheses(s):
        stack = []
        cp = {}
        for j, c in enumerate(s):
            if c == "(":
                stack.append(j)
            elif c == ")":
                i = stack.pop()
                cp[i] = j - i
        assert not stack
        return cp

    def _compile(start, end):
        o, c = query.find("(", start, end), query.find(")", start, end)
        if o >= 0 and c >= 0:
            # first pass; replace all top level conditions -> 'placholder-*'
            new_expr, placeholders = _placehold_parantehsized_expr(start, end)
            # second pass; we should not expect any paraneteses now
            tags = _compile_base_base(new_expr, True)
            for p, (s, e) in placeholders.items():
                placeholders[p] = _compile(s, e)
            return _replace_placeholder_dfs(tags, placeholders)
        elif o < 0 and c < 0:
            return _compile_base_base(query[start:end])
        else:
            raise ValueError("unclosed paranthesis")

    def _compile_base_base(expr, assert_no_parans=False):
        assert not assert_no_parans or expr.find(")") < 0 and expr.find(")") < 0, expr
        query_pat = r"^(?:\s*(.+?)\s*(>=|<=|==|!=|=|>|<)\s*(.+?)\s*|\s*(placeholder-\w{8}-\w{4}-\w{4}-\w{4}-\w{12})\s*)$"  # noqa: E501
        split_pat = r"\s(and|or|\|\||\||&&|&)\s"
        conditions = re.split(split_pat, expr)
        m = re.match(query_pat, conditions[0])
        tags = _make_tag_condition(*m.groups())
        if m is None:
            raise ValueError("invalid tag query")
        for boolop, cond in zip(conditions[1::2], conditions[2::2]):
            m = re.match(query_pat, cond)
            tags = {BOOLOP[boolop]: [_make_tag_condition(*m.groups()), tags]}
        return tags

    def _replace_placeholder_dfs(tags, placeholders):
        if isinstance(tags, ComparableCondition):
            return tags
        elif isinstance(tags, PlaceholderCondition):
            return placeholders[tags.name]
        elif isinstance(tags, dict):
            for k, v in tags.items():
                return {k: [_replace_placeholder_dfs(vv, placeholders) for vv in v]}
        else:
            raise ValueError("tags is of unexpected type")

    def _placehold_parantehsized_expr(start, end):
        nonlocal cp_indices
        new_s = ""
        placeholders = {}
        while start < end:
            o = query.find("(", start, end)
            if o < 0:
                new_s += query[start:end]
                break
            c = o + cp_indices[o]
            plid = f"placeholder-{uuid.uuid1(o)}"
            placeholders[plid] = (o + 1, c)
            new_s += f"{query[start:o-1]} {plid} " if o - 1 > start else f" {plid} "
            start = c + 1
        return new_s, placeholders

    cp_indices = _match_parantheses(query)
    return _compile(0, len(query))


def to_sqlalchemy_query(tags):
    if isinstance(tags, ComparableCondition):
        if isinstance(tags.right, (float, int)) or tags.right.isfloat():
            Tag = NumberTag
            val = float(tags.right)
        elif isinstance(tags.right, bool) or tags.right in (
            "true",
            "True",
            "false",
            "False",
        ):
            Tag = BoolTag
            val = True if tags.right in ("true", "True", True) else False
        elif isinstance(tags.right, str):
            Tag = StrTag
            val = tags.right
        return and_(
            Tag.name == tags.left,
            getattr(Tag.value, tags.op)(val),
            Tag.position_id == Position.id,
        )
    elif isinstance(tags, dict):
        for k, v in tags.items():
            return getattr(sqlalchemy, k)(to_sqlalchemy_query(vv) for vv in v)
    else:
        raise ValueError("tags is of unexpected type")


class PositionSelectRequest(_PositionSelectRequest):
    @validator("symbol")
    def valid_symbol(cls, v) -> str:
        if v is None or v == "":
            return None
        if not v.strip().isalpha():
            raise ValueError(
                "Symbol consists of non-alphabetical character(s). "
                "Valid examples include AAPL, ZM, and etc"
            )
        return v

    @validator("status")
    def valid_status(cls, v) -> str:
        if v is None or v == "":
            return ["open", "close"]
        if "open".startswith(v.lower()):
            return ["open"]
        if "close".startswith(v.lower()):
            return ["close"]
        raise ValueError('Status can only be "open" or "close"')

    @validator("position")
    def valid_position(cls, v) -> str:
        if v is None or v == "":
            return None
        if "long".startswith(v.lower()):
            return ["long"]
        if "short".startswith(v.lower()):
            return ["short"]
        raise ValueError('Position can only be "long" or "short"')

    @validator("quantity")
    def valid_quantity(cls, v):
        if v is None or v == "":
            return None
        if v.startswith(tuple(OP2C.keys())) and v[2:].strip().isdecimal():
            return OPPair(OP2C[v[:2]], v[2:].strip().toInt())
        elif v.startswith(tuple(OP1C.keys())) and v[1:].strip().isdecimal():
            return OPPair(OP1C[v[:1]], v[1:].strip().toInt())
        elif v.strip().isdecimal():
            return OPPair(OP1C["="], v.strip().toInt())
        else:
            raise ValueError("Quantity must be an integer, e.g. 1, 5, 10 and etc.")

    @validator("open_price")
    def valid_open_price(cls, v):
        if v is None or v == "":
            return None
        if v.startswith(tuple(OP2C.keys())) and v[2:].strip().isfloat():
            return OPPair(OP2C[v[:2]], float(v[2:].strip()))
        elif v.startswith(tuple(OP1C.keys())) and v[1:].strip().isfloat():
            return OPPair(OP1C[v[:1]], float(v[1:].strip()))
        elif v.strip().isfloat():
            return OPPair(OP1C["="], float(v.strip()))
        else:
            raise ValueError(
                "Open price is not valid; it must a a valid decimal. e.g. 121.3"
            )

    @validator("open_at")
    def valid_open_at(cls, v):
        if v is None or v == "":
            return None
        if v.startswith(tuple(OP2C.keys())):
            try:
                time = datetime.fromisoformat(v[2:].strip())
            except ValueError as e:
                raise ValueError(
                    "Open at is not a valid date; Date must follow ISO format, "
                    "e.g. 2021-02-03 09:35"
                ) from e
            else:
                return OPPair(OP2C[v[:2]], time)
        elif v.startswith(tuple(OP1C.keys())):
            try:
                time = datetime.fromisoformat(v[1:].strip())
            except ValueError as e:
                raise ValueError(
                    "Open at is not a valid date; Date must follow ISO format, "
                    "e.g. 2021-02-03 09:35"
                ) from e
            else:
                return OPPair(OP1C[v[:1]], time)
        else:
            try:
                time = datetime.fromisoformat(v.strip())
            except ValueError as e:
                raise ValueError(
                    "Open at is not a valid date; Date must follow ISO format, "
                    "e.g. 2021-02-03 09:35"
                ) from e
            else:
                return OPPair(OP1C["="], time)

    @validator("close_at")
    def valid_close_at(cls, v):
        if v is None or v == "":
            return None
        if v.startswith(tuple(OP2C.keys())):
            try:
                time = datetime.fromisoformat(v[2:].strip())
            except ValueError as e:
                raise ValueError(
                    "Open at is not a valid date; Date must follow ISO format, "
                    "e.g. 2021-02-03 09:35"
                ) from e
            else:
                return OPPair(OP2C[v[:2]], time)
        elif v.startswith(tuple(OP1C.keys())):
            try:
                time = datetime.fromisoformat(v[1:].strip())
            except ValueError as e:
                raise ValueError(
                    "Open at is not a valid date; Date must follow ISO format, "
                    "e.g. 2021-02-03 09:35"
                ) from e
            else:
                return OPPair(OP1C[v[:1]], time)
        else:
            try:
                time = datetime.fromisoformat(v.strip())
            except ValueError as e:
                raise ValueError(
                    "Open at is not a valid date; Date must follow ISO format, "
                    "e.g. 2021-02-03 09:35"
                ) from e
            else:
                return OPPair(OP1C["="], time)

    @validator("tags")
    def valid_tags(cls, v):
        if v is None or v == "":
            return None
        try:
            res = compile_query(v)
        except (AttributeError, ValueError, IndexError) as e:
            raise ValueError("invalid tag query") from e
        return res


class PositionCreateRequest(BaseModel):
    status: str
    position: str
    quantity: int
    symbol: str
    open_price: float
    close_price: Optional[float] = None
    open_at: str
    close_at: Optional[str] = None
    tags: Optional[Dict] = None

    @validator("position")
    def valid_poisiton(cls, v: str):
        if v.lower() not in ("long", "short"):
            raise ValueError("Position can only be long/short")
        return v.lower()

    @validator("status")
    def valid_status(cls, v: str):
        if v.lower() not in ("open", "close"):
            raise ValueError("Status can only be open/close")
        return v.lower()

    @validator("quantity")
    def valid_quanity(cls, v: int):
        if not isinstance(v, int):
            raise ValueError("Quanity needs to be an integer")
        return int(v)

    @validator("symbol")
    def valid_symbol(cls, v: str):
        if not v.isalpha():
            raise ValueError("Symbol cannot consist of non-alphabetical character(s)")
        return v

    @validator("open_price")
    def valid_open_price(cls, v: float):
        if not isinstance(v, float):
            raise ValueError("Close Price is not a valid decimal")
        return v

    @validator("close_price")
    def valid_close_price(cls, v: float):
        if not isinstance(v, float):
            raise ValueError("Close Price is not a valid decimal")
        return v

    @validator("open_at")
    def valid_open_at(cls, v: str):
        try:
            time = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Open At is not a valid ISO-formatted datetime")
        else:
            return time

    @validator("close_at")
    def valid_close_at(cls, v):
        try:
            time = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Close At is not a valid ISO-formatted datetime")
        else:
            return time

    @validator("tags")
    def valid_tags(cls, v: str):
        if not isinstance(v, str):
            raise ValueError("Tag cannot consist of non-alphabetical character(s)")
        return v


class PositionItem(BaseModel):
    id: int
    symbol: str
    position: str
    status: str
    quantity: int
    open_price: float
    final_price: float
    percent_return: float
    open_at: datetime
    close_at: datetime
    tags: Optional[Dict] = None
    updated_at: datetime


class PositionsResponse(Response):
    data: Dict[str, PositionItem]
    total_count: int


class PositionDetailsResponse(Response):
    id: int
    symbol: str
    position: str
    status: str
    quantity: int
    open_price: float
    final_price: float
    percent_return: float
    # tags: Optional[Dict] = None
    updated_at: datetime
    d: Signal
    d3: Signal
    w: Signal
    m: Signal
    y: Signal


class _PriceRequest(BaseModel):
    position_query: Optional[str]
    page: Optional[int] = None
    limit: Optional[int] = None
    last_id: Optional[int] = None


class PriceRequest(_PriceRequest):
    @validator("position_query")
    def valid_position_query(cls, v: str) -> List[str]:
        if not v:
            return None
        if "," in v:
            return [i.strip() for i in v.split(",")]
        return [v.strip()]

    @validator("page")
    def valid_page(cls, v: int):
        if v is None:
            return v
        if v < 0:
            raise ValueError("page number cannot be negative")
        return v

    @validator("limit")
    def valid_limit(cls, v: int):
        if v is None:
            return v
        if v < 0:
            raise ValueError("limit cannot be negative")
        return v

    @validator("last_id")
    def valid_last_id(cls, v: int):
        if v is None:
            return v
        if v < 0:
            raise ValueError("last_id cannot be negative")
        return v


class PriceItem(BaseModel):
    id: int
    symbol: str
    status: str
    position: str
    quantity: int
    pre_signal: List[Datum]
    post_signal: List[Datum]
    signal: List[Datum]
    percent_change: float
    dollar_change: float
    # TODO remove
    tags: Optional[Dict]


class PriceResponse(Response):
    data: List[PriceItem]


class SymbolRequest(BaseModel):
    name: str


class _ProfitRequest(BaseModel):
    ids: Optional[str] = None
    time: Optional[str] = None


class ProfitRequest(_ProfitRequest):
    @validator("time")
    def valid_time(cls, v: str):
        if v is None:
            return v

        return datetime.fromisoformat(v)

    @validator("ids")
    def valid_ids(cls, v: str):
        if v is None:
            return v

        return v.split(",")
