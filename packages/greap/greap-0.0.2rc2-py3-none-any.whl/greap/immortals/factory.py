def immortal_factory(type_: str):
    """
    A factory to return the correponding immortal type based type specified.

    :params type_: type of the immortal to create
    """
    if type_ == "controller":
        from .controller import Controller

        return Controller

    if type_ == "log_servicer":
        from .log_servicer import LogServicer

        return LogServicer

    if type_ == "load_balancer":
        from .load_balancer import LoadBalancer

        return LoadBalancer

    if type_ == "server":
        from .server import Server

        return Server

    if type_ == "prefetcher":
        from .prefetcher import Prefetcher

        return Prefetcher

    if type_ == "backtest_quote_price_feeder":
        from .backtest_quote_price_feeder import BacktestQuotePriceFeeder

        return BacktestQuotePriceFeeder

    if type_ == "immortal":
        from .base import Immortal

        return Immortal

    if type_ == "connector":
        from .connector import Connector

        return Connector

    raise TypeError(f"Given type {type_} is not supported")
