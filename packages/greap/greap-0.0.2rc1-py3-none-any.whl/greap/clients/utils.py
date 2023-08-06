from datetime import datetime
import bisect
import itertools
from collections import namedtuple, deque
from pytz import timezone


tz = timezone("America/New_york")


PriceTuple = namedtuple(
    "PriceTuple", ["time", "open", "high", "low", "close", "volume", "vwap"]
)


QuoteTuple = namedtuple("QuoteTuple", ["open", "close", "high", "low", "preclose"])


class Buffer(object):
    def __init__(self, capacity):
        self._time_list = deque()
        self._val_list = deque()
        self._capacity = capacity
        self._size = 0
        self._max = None

    def insert(self, time: datetime, val: float):
        if self._capacity <= self._size:
            self.evict()

        self._time_list.append(time)
        self._val_list.append(val)
        self._size += 1

    def get(self, index):
        if not self._val_list:
            return None
        return self[index]

    def max(self):
        if self._max is not None:
            return self._max.val
        self._max = max(self._val_list)
        return self._max.val

    def evict(self):
        self._time_list.popleft()
        self._val_list.popleft()
        self._max = None
        self._size -= 1

    def __iter__(self):
        for k in self._time_list:
            yield k

    def __repr__(self):
        return (
            f"len of buffer: {len(self._val_list)}, "
            f"last item: {list(zip(self._time_list, self._val_list))[-1:]}"
        )

    def __str__(self):
        return self.__repr__()

    def items(self):
        for k, v in zip(self._time_list, self._val_list):
            yield k, v

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        if isinstance(index, int):
            time = self._time_list[index]
            val = self._val_list[index]
        elif isinstance(index, slice):
            if (
                index.start is not None
                and index.start < 0
                and len(self) + index.start > 0
            ):
                start = len(self) + index.start
            elif index.start is not None and index.start < 0:
                return [], []
            else:
                start = index.start

            if index.stop is not None and index.stop < 0 and len(self) + index.stop > 0:
                stop = len(self) + index.stop
            elif index.stop is not None and index.stop < 0:
                return [], []
            else:
                stop = index.stop

            time = itertools.islice(self._time_list, start, stop, index.step)

            val = itertools.islice(self._val_list, start, stop, index.step)
        else:
            raise IndexError("invalid index")
        return list(time), list(val)

    def index_at(self, time):
        return bisect.bisect(self._time_list, time)
