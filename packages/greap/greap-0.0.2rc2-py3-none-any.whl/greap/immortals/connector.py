import sqlalchemy
from datetime import datetime
import asyncio
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlalchemy import select, update
from ..db import create_engine
from ..models import Position, PositionMetadata
from ..timer import Timer
from ..logger import Logger
from ..diff_subscriber import DbDiffSubscriber
from ..clients import create_order_factory, get_order_factory


async def _open_position(position, api):
    return await api(
        position.symbol,
        position.quantity,
        position.submit_open_price,
        position.stop_open_price,
        position.submit_open_at,
    )


async def _close_position(position, api):
    return await api(
        position.symbol,
        position.quantity,
        position.submit_close_price,
        position.stop_close_price,
        position.submit_close_at,
        close=True,
    )


async def _create_order(position, api):
    if position.status == "submit_open":
        return await _open_position(position, api)
    elif position.status == "submit_close":
        return await _close_position(position, api)
    else:
        raise ValueError(f"invalid status to place order, received: {position.status}")


async def _get_and_update(pos_metadata, session, api, logger, close: bool = False):
    if close:
        order = api(pos_metadata.close_order_id)
        filled_at = datetime.fromisoformat(order.get("filled_at"))
        filled_avg_price = float(order.get("filled_avg_price"))
        if filled_avg_price is not None:
            await session.execute(
                update(Position)
                .where(Position.id == pos_metadata.position_id)
                .values(close_price=filled_avg_price)
                .values(status="close")
                .values(close_at=filled_at)
            )
            await session.execute(
                update(PositionMetadata)
                .where(PositionMetadata.position_id == pos_metadata.position_id)
                .values(close_at=filled_at)
            )
            return True
    else:
        order = api(pos_metadata.open_order_id)
        filled_at = datetime.fromisoformat(order.get("filled_at"))
        filled_avg_price = float(order.get("filled_avg_price"))
        if filled_avg_price is not None:
            await session.execute(
                update(Position)
                .where(Position.id == pos_metadata.position_id)
                .values(open_price=filled_avg_price)
                .values(status="open")
                .values(open_at=filled_at)
            )
            await session.execute(
                update(PositionMetadata)
                .where(PositionMetadata.position_id == pos_metadata.position_id)
                .values(open_at=filled_at)
            )
            return True
    return False


def Connector(
    id: str,
    database_addr: str,
    # in_ctrl_addr: str,
    # out_ctrl_addr: str,
    timer_args: Dict,
    sink: str,
    sleep_interval: float = 1,
    **kwargs,
):
    timer = Timer(**timer_args)
    logger = Logger(id, timer)
    logger.info(f"in connector , sleep_interval: {sleep_interval}")
    from greap.models import Position, PositionMetadata

    try:
        SQLModel.metadata.create_all(create_engine(database_addr))
    except sqlalchemy.exc.OperationalError:
        pass

    conn = create_async_engine(
        database_addr.replace("sqlite://", "sqlite+aiosqlite://").replace(
            "mysql://", "mysql+aiomysql://"
        )
    )
    create_order_api = create_order_factory(sink)
    get_order_api = get_order_factory(sink)
    queue = asyncio.Queue()

    ds = DbDiffSubscriber(conn, timer, sleep_interval=sleep_interval)

    @ds.observe(cls=Position, primary_key=Position.id, attr=Position.status)
    async def db_diff_constrainer(old: dict, new: dict):
        async with AsyncSession(conn) as sess:
            positions = await sess.execute(
                select(Position).where(Position.id.in_(new.keys()))
            )
            for (pos,) in positions:
                logger.debug(f"detected diff for position with id: {pos.id}")
                if pos.status in {"submit_open", "submit_close"}:
                    logger.debug(
                        f"put position {pos} to queue for downstream processing"
                    )
                    await queue.put(pos)

    async def create_order_constrainer():
        async with AsyncSession(conn) as sess:
            while pos := await queue.get():
                order_id, submitted_at, close = await _create_order(
                    pos, create_order_api
                )
                logger.debug(
                    f'created a {"open" if not close else "close"} '
                    f"order with order_id: {order_id} to the broker"
                )
                if close:
                    stmt = (
                        update(PositionMetadata)
                        .where(PositionMetadata.position_id == pos.id)
                        .values(close_order_id=order_id)
                        .values(submit_close_at=submitted_at)
                    )
                    await sess.execute(stmt)
                else:
                    pos_metadata = PositionMetadata(
                        position_id=pos.id,
                        open_order_id=order_id,
                        submit_open_at=submitted_at,
                    )
                    sess.add(pos_metadata)
                await sess.commit()

    async def db_exchange_constrainer():
        async with AsyncSession(conn) as sess:
            while True:
                try:
                    metas = (await sess.execute(select(PositionMetadata))).all()
                except sqlalchemy.exc.OperationalError:
                    pass
                else:
                    for (meta,) in metas:
                        updated = False
                        if meta.submit_open_at is not None and meta.open_at is None:
                            updated = await _get_and_update(
                                meta, sess, get_order_api, logger
                            )
                            if updated:
                                logger.info(
                                    f"position {meta.position_id} is filled to open!"
                                )
                        elif meta.submit_close_at is not None and meta.close_at is None:
                            updated = await _get_and_update(
                                meta, sess, get_order_api, logger, close=True
                            )
                            if updated:
                                logger.info(
                                    f"position {meta.position_id} is filled to close!"
                                )

                    await sess.commit()
                await timer.sleep(sleep_interval)

    loop = asyncio.get_event_loop()
    done, pending = loop.run_until_complete(
        asyncio.wait(
            [
                ds.run_event_loop(),
                create_order_constrainer(),
                db_exchange_constrainer(),
            ],
            return_when=asyncio.FIRST_EXCEPTION,
        )
    )

    exception = None
    for task in done | pending:
        try:
            exception = task.exception()
        except asyncio.exceptions.InvalidStateError:
            pass

    if exception:
        logger.debug(f"raise exception {exception} from immortal")
        raise exception
