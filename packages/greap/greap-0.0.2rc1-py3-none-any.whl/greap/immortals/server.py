from collections import namedtuple
from datetime import timedelta
from typing import Optional, Dict, List
import uvicorn

import sqlalchemy
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from pydantic.error_wrappers import ValidationError
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from sqlmodel import Session, SQLModel
from ..db import create_engine
import zmq

from ..zmq.socket import AsyncContext
from .signals import (
    ReadyToStart,
)
from ..models import (
    Position,
    MissingPrice,
    _InvestedRequest,
    InvestedRequest,
    ProfitItem,
    InvestedResponse,
    _PositionSelectRequest,
    PositionSelectRequest,
    PositionCreateRequest,
    PositionItem,
    PositionsResponse,
    _PriceRequest,
    PriceRequest,
    PriceItem,
    PriceResponse,
    PositionDetailsResponse,
    Response,
)
from ..timer import Timer
from .validator import Validator
from ..api import ExchangeAPI, zip_positions
from ..profiler import timeit


NUM_DATAPOINTS = 390

TimeHorizon = namedtuple(
    "TimeHorizon", ["name", "interval_length", "start_at", "delta"]
)

timeHorizons = list(
    map(
        TimeHorizon._make,
        [
            ("d", 1, lambda now: now.prev_open_time(), timedelta(days=1)),
            (
                "d3",
                3,
                lambda now: now - timedelta(days=3),
                timedelta(days=3),
            ),
            (
                "w",
                10,
                lambda now: now - timedelta(days=7),
                timedelta(days=7),
            ),
            (
                "m",
                40,
                lambda now: now - timedelta(weeks=4),
                timedelta(weeks=4),
            ),
            (
                "y",
                500,
                lambda now: now - timedelta(weeks=52),
                timedelta(weeks=52),
            ),
        ],
    )
)


def get_position_items(
    api: ExchangeAPI, req: PositionSelectRequest
) -> Dict[int, PositionItem]:
    pagination_args = get_pagination_args(req)
    positions = api.position.items(request=req, pagination_args=pagination_args)
    symbols = {pos.symbol for pos in positions}
    now = api.now(minute_only=True)

    final_price = {
        symbol: api.price.take_one(symbol=symbol, end_at=now, precision=5)
        for symbol in symbols
    }

    result = {}
    for pos in positions:
        try:
            percent_return = (
                ((pos.close_price or final_price[pos.symbol]) - pos.open_price)
                * 100
                / pos.open_price
            )
        except ZeroDivisionError:
            percent_return = 0

        result[pos.id] = PositionItem(
            id=pos.id,
            status=pos.status,
            open_at=pos.open_at,
            close_at=pos.close_at,
            symbol=pos.symbol,
            position=pos.position,
            quantity=pos.quantity,
            open_price=pos.open_price,
            final_price=pos.close_price or final_price[pos.symbol],
            percent_return=percent_return,
            tags={
                k: "{:.2f}".format(v) if isinstance(v, (int, float)) else v
                for k, v in pos.tags.items()
            },
            updated_at=pos.updated_at,
        )
    return result


def get_pagination_args(req) -> Optional[Dict]:
    if req.limit is not None and req.page is not None:
        return {"page": req.page, "limit": req.limit, "last_id": req.last_id}
    elif req.limit is None and req.page is None:
        return None
    else:
        raise ValueError("both page and limit needs to be provided")


def get_price_items(api: ExchangeAPI, req) -> List[PriceItem]:
    pagination_args = get_pagination_args(req)
    positions = api.position.items(
        id=req.position_query, pagination_args=pagination_args
    )
    with timeit("get_prices"):
        pos_to_prices = api.position.get_prices_from_open_until_close(
            num_points=NUM_DATAPOINTS,
            positions=positions,
            min_extra_duration=10,
            extra_duration_percent=0.15,
        )
    return [
        PriceItem(
            id=pos.id,
            position=pos.position,
            status=pos.status,
            symbol=pos.symbol,
            pre_signal=pos_to_prices[pos.id].pre,
            signal=pos_to_prices[pos.id].actual,
            post_signal=pos_to_prices[pos.id].post,
            quantity=pos.quantity,
            dollar_change=(
                pos_to_prices[pos.id].actual[-1].value
                - pos_to_prices[pos.id].actual[0].value
            )
            if len(pos_to_prices[pos.id].actual) > 0
            else 0,
            percent_change=(
                pos_to_prices[pos.id].actual[-1].value
                - pos_to_prices[pos.id].actual[0].value
            )
            / pos_to_prices[pos.id].actual[0].value
            * 100
            if len(pos_to_prices[pos.id].actual) > 0
            and pos_to_prices[pos.id].actual[0].value > 0  # noqa: E501
            else 0,
            tags=pos.tags,
        )
        for pos in positions
        if pos.id in pos_to_prices
    ]


def get_invested_response(
    api: ExchangeAPI, id: Optional[List[int]] = None
) -> InvestedResponse:
    now = api.now(minute_only=True)

    results = {"type": "success", "now": api.now()}
    with timeit("get_invested"):

        with timeit("get_invested - get latest value"):
            t, invested_now = api.invested.take_one(
                end_at=now << 0, positions={"id": id, "status": "open"}
            )

        with timeit("get_profit - first time get positions"):
            positions = api.position.items(
                id=id, return_timestamp=True, return_tags=False
            )

        with timeit("get_profit - zip_positions"):
            positions = zip_positions(positions)

        for (horizon, interval_length, start_at, _) in timeHorizons:
            signal = api.profit.take_every(
                positions=positions,
                start_at=start_at(now),
                end_at=now,
                interval_length=interval_length,
            )
            # ensure signal has length > 2
            signal = signal or [[0, 0]]
            results[horizon] = ProfitItem(
                last_updated=now,
                signal=signal,
                invested=invested_now,
                dollar_change=(signal[-1][1] - signal[0][1]),
            )
    return InvestedResponse.parse_obj(results)


def get_position_details_response(api: ExchangeAPI, position_id: int):
    pos = api.position.get(position_id)
    if pos is None:
        return Response(type="error", now=api.now())

    now = api.now(minute_only=True)

    data = {
        "type": "success",
        "now": now,
        "id": pos.id,
        "symbol": pos.symbol,
        "position": pos.position,
        "status": pos.status,
        "quantity": pos.quantity,
        "open_price": pos.open_price,
        "final_price": pos.close_price,
        "updated_at": pos.updated_at,
    }

    duration = (pos.close_at if pos.status == "close" else now) - pos.open_at

    for name, interval_length, _, delta in timeHorizons:
        min_extra_duration = delta.total_seconds() // 60
        extra_duration_percent = delta.total_seconds() / duration.total_seconds()

        data[name] = api.position.get_prices_from_open_until_close(
            num_points=NUM_DATAPOINTS,
            positions=pos.dict(),
            min_extra_duration=min_extra_duration,
            extra_duration_percent=extra_duration_percent,
        )[position_id]

    # get final price and calculate precent return
    data["final_price"] = data["final_price"] or data["d"].actual[-1].value
    try:
        data["percent_return"] = (
            (data["final_price"] - data["open_price"]) * 100 / data["open_price"]
        )
    except ZeroDivisionError:
        data["percent_return"] = 0

    return PositionDetailsResponse.parse_obj(data)


app = FastAPI()


def Server(
    id: str,
    database_addr: str,
    in_ctrl_addr: str,
    out_ctrl_addr: str,
    timer_args: Dict,
    port: int = 80,
    **kwargs,
):

    timer = Timer(**timer_args)
    zmqctx = AsyncContext()
    in_ctrl_sock = zmqctx.socket(zmq.PULL)
    in_ctrl_sock.bind(in_ctrl_addr)

    out_ctrl_sock = zmqctx.socket(zmq.PUSH)
    out_ctrl_sock.connect(out_ctrl_addr)

    conn = create_engine(database_addr)

    try:
        SQLModel.metadata.create_all(conn)
    except sqlalchemy.exc.OperationalError:
        pass

    is_updating = can_open = lambda: True
    get_version = lambda: 1
    api = ExchangeAPI(
        validator=Validator(),
        can_open=can_open,
        get_version=get_version,
        is_updating=is_updating,
        db_conn=conn,
        timer=timer,
    )
    global app

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": jsonable_encoder(exc.errors())},
        )

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/invested")
    async def get_invested(req: _InvestedRequest = Depends()):
        try:
            req = InvestedRequest.parse_obj(req.dict())
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors) from e

        # "Investing" shows the total amount of money opened
        # line graph shows the cumulative profit
        # at every time tick, accumulate the (curr_price - open_price)
        # for all positions in the collection
        return get_invested_response(api, req.ids)

    @app.get("/prices")
    async def get_position_prices(req: _PriceRequest = Depends()):
        try:
            req = PriceRequest.parse_obj(req.dict())
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors) from e
        ret = PriceResponse(
            data=get_price_items(api, req), type="success", now=api.now()
        )
        return ret

    @app.get("/start")
    async def start():
        await out_ctrl_sock.send(ReadyToStart())

    @app.get("/positions")
    async def get_positions(req: _PositionSelectRequest = Depends()):
        try:
            req = PositionSelectRequest.parse_obj(req.dict())
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors) from e

        return PositionsResponse(
            type="success",
            data=get_position_items(api, req),
            total_count=api.position.count(req),
            now=api.now(),
        )

    @app.get("/positions/{pId}")
    async def get_position_details(pId: int):
        return get_position_details_response(api, pId)

    @app.post("/positions")
    async def create_positions(req: List[PositionCreateRequest]):
        data = []
        with Session(conn) as sess:
            for r in req:
                d = Position(
                    status=r.status,
                    position=r.position,
                    quantity=r.quantity,
                    symbol=r.symbol,
                    open_price=r.open_price,
                    open_at=r.open_at,
                    tag=r.tag,
                    updated_at=r.open_at,
                )
                sess.merge(d)
                sess.commit()
                data.append(d)

        return {"data": data}

    @app.delete("/positions")
    async def delete_all_positions():
        Position.__table__.drop(conn)
        SQLModel.metadata.create_all(conn)
        return Response(type="success")

    @app.delete("/missing-prices")
    async def delete_missing_prices():
        MissingPrice.__table__.drop(conn)
        return Response(type="success")

    @app.get("/symbols")
    async def get_all_symbols():
        return api.symbol.items()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],  # Allows all headers
    )

    print(port)
    uvicorn.run(
        "greap.immortals.server:app", host="0.0.0.0", port=port, log_level="info"
    )
