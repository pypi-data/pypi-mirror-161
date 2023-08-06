from datetime import datetime
from typing import Optional
from alpaca_trade_api.rest import REST
from pyrfc3339 import generate, parse  # noqa: F401

API_KEY = "PKQUX24LLOM2KP27B3LU"
SECRETS = "4haBGSbIHxX3PJYDvtb33VfPsWZx4xX9Sz8O20pZ"
api = REST(API_KEY, SECRETS)


async def create_order(
    symbol: str,
    quantity: str,
    price: float,
    stop_price: float,
    submit_at: Optional[datetime] = None,
    close: bool = False,
):
    resp = api.submit_order(
        symbol=symbol,
        qty=quantity,
        side="buy" if not close else "sell",
        type="stop_limit",
        time_in_force="day",
        limit_price=price,
        stop_price=stop_price,
    )
    time = (
        datetime.fromisoformat(resp["created_at"]).astimezone(tz).replace(tzinfo=None)
    )
    return resp["id"], time, close


def get_order(order_id: str):
    return api.get_order(order_id)
