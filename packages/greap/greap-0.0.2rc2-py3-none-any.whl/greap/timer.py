import pytz
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Union
from .models import OPEN_HOURS_DURATION_COUNT, NEXT_DAY_COUNT


RELAX_TIME = 5

nytz = pytz.timezone("America/New_york")


class Timer:
    def __init__(
        self,
        mode: str = "auto",
        now: Optional[Union[str, datetime]] = None,
        now_actual: Optional[float] = None,
        scale: Optional[int] = None,
        fast_forward: bool = False,
    ):
        now = now or datetime.now()
        self._start = now if isinstance(now, datetime) else datetime.fromisoformat(now)
        self._start_actual = now_actual or time.time()
        self._scale = scale or 1
        self._fast_forward = fast_forward
        self._last = None

    def now(self, tz=nytz, minute_only: bool = False, at: Optional[float] = None):
        at = at or time.time()
        delta = (at - self._start_actual) * self._scale

        if not self._fast_forward:
            now = self._start + timedelta(seconds=delta)
        else:
            now = self._start
            if not now.is_open():
                now = now.next_open_time() - timedelta(minutes=RELAX_TIME)

            time_to_close = (now.next_close_time() - now).total_seconds()

            while delta >= time_to_close:
                delta -= time_to_close
                if now + timedelta(seconds=time_to_close) >= now.next_day(
                    weekday=4, hour=16, minute=1
                ):
                    now += timedelta(days=2)
                now += timedelta(
                    seconds=time_to_close + (NEXT_DAY_COUNT - RELAX_TIME) * 60
                )
                time_to_close = (OPEN_HOURS_DURATION_COUNT + RELAX_TIME) * 60

            now += timedelta(seconds=delta)

        return (
            now.astimezone(tz).replace(tzinfo=None)
            if not minute_only
            else now.astimezone(tz).replace(tzinfo=None, second=0, microsecond=0)
        )

    @staticmethod
    def verify_args(
        mode: str = "auto",
        now: Optional[str] = None,
        now_actual: Optional[float] = None,
        scale: Optional[int] = None,
        fast_forward: bool = True,
    ):
        if scale is not None:
            assert isinstance(
                scale, (float, int)
            ), f"scale must be a float or int, got {type(scale)}"
            assert scale > 0, f"scale must be greater than 0, got {scale}"

        assert mode in {
            "auto",
            "manual",
        }, f"timer mode is unknown. it can only be auto or manual, got {mode}"

        if now is not None:
            t = datetime.fromisoformat(now)
            assert (
                t.tzinfo is not None
            ), "time zone (e.g. -05:00 or +08:00) needs to be provided"

            assert now_actual is not None, "actual time now needs to be provided"

    async def sleep(self, seconds: int):
        await asyncio.sleep(self.to_real(seconds))

    async def maintain_interval(self, seconds: float):
        if self._last is None:
            seconds = self.to_real(seconds)
            await asyncio.sleep(seconds)
            self._last = self.now()
            return True
        else:
            time_elapsed = (self.now() - self._last).seconds
            delta = self.to_real(seconds - time_elapsed)
            if delta < 0:
                self._last = self.now()
                return False
            await asyncio.sleep(delta)
            self._last = self.now()
            return True

    def to_real(self, scaled):
        return scaled / self._scale

    def to_scaled(self, real):
        return real * self._scale

    def close(self, **kwargs):
        pass
