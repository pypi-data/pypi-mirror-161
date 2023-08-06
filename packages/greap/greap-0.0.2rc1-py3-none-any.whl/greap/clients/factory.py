def get_historic_prices_factory(name: str):
    if name == "webull":
        from .wb import get_historic_prices
    elif name == "backtest":
        from .backtest import get_historic_prices
    else:
        raise ValueError(
            f"invalid data source - can only be either webull or backtest, got {name}"
        )
    return get_historic_prices


def get_quote_price_factory(name: str):
    if name == "webull":
        from .wb import get_quote_price
    elif name == "backtest":
        from .backtest import get_quote_price
    else:
        raise ValueError(
            f"invalid data source - can only be either webull or backtest, got {name}"
        )
    return get_quote_price


def create_order_factory(name: str):
    if name == "alpaca":
        from .alpaca import create_order

    elif name == "backtest":
        from .backtest import create_order
    else:
        raise ValueError(
            f"invalid data source - can only be either alpaca or backtest, got {name}"
        )
    return create_order


def get_order_factory(name: str):
    if name == "alpaca":
        from .alpaca import get_order

    elif name == "backtest":
        from .backtest import get_order
    else:
        raise ValueError(
            f"invalid data source - can only be either alpaca or backtest, got {name}"
        )
    return get_order
