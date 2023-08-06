from typing import Optional, Callable
import time
from contextlib import contextmanager


@contextmanager
def timeit(task_name: str, log_fn: Optional[Callable] = None):
    t1 = time.time()
    yield
    t2 = time.time()
    if log_fn:
        log_fn(f"{task_name} takes {t2 - t1} seconds")
    else:
        print(f"{task_name} takes {t2 - t1} seconds")
