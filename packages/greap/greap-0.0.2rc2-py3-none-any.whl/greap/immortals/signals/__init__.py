from typing import Optional

from greap.types import payload


@payload
class Signal:
    ...


@payload
class StartRequest(Signal):
    ...


@payload
class ReadyToStart(Signal):
    ...


@payload
class PrefetchCompleted(Signal):
    ...


@payload
class DisableOpen(Signal):
    ...


@payload
class EnableOpen(Signal):
    ...


@payload
class Stop(Signal):
    ...


@payload
class FetchLockAcquire(Signal):
    ...


@payload
class FetchLockRelease(Signal):
    updated: bool


@payload
class FetchLockAcquireStatus(Signal):
    ok: bool


@payload
class FetchLockReleaseStatus(Signal):
    ok: bool


@payload
class FetchDataStatus(Signal):
    updating: bool
    version: Optional[int] = None
