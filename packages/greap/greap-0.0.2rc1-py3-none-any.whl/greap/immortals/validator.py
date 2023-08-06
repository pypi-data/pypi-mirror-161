import inspect
from collections import defaultdict
from typing import Optional

from ..logger.logger import Logger


class Validator:
    def __init__(self, allow_force_restart: bool = False):
        self._errors = {}
        self._exceptions = []
        self._versions = defaultdict(dict)
        self._updating_statuses = defaultdict(dict)
        self._info = None
        self._allow_force_restart = allow_force_restart
        self._is_running = False

    def start(self, reset=True):
        if self._is_running and self._allow_force_restart:
            raise ValueError(
                "cannot not start a running validator"
                "where force restart is not allowed"
            )
        self._is_running = True
        self.reset()

    def reset(self):
        self._errors.clear()
        self._versions.clear()
        self._updating_statuses.clear()
        self._info = None

    def stop(self):
        self._is_running = False

    def validate(
        self,
        ensure_atomic: bool = True,
        reset_after_validate: bool = True,
        logger: Optional[Logger] = None,
    ):
        is_valid = True
        if self._errors:
            self._info = "\n".join(": ".join(item) for item in self._errors.items())
            is_valid = False

        if not ensure_atomic and is_valid:
            return True

        versions = set(v for d in self._versions.values() for v in d.values())

        updating_statues = set(us for d in self._versions.values() for us in d.values())

        if len(versions) > 1:
            self._info = "version has been updated but expect atomic operation"
            is_valid = False

        elif len(updating_statues) > 1:
            self._info = (
                "db is updating while data is fetched but expect atomic operation"
            )
            is_valid = False

        if logger is not None and self._info:
            logger.error(self._info)

        if reset_after_validate:
            self.reset()

        return is_valid

    def add_error(self, error: str, caller_name: Optional[str] = None):
        if not self._is_running:
            return
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller_name = caller_name or calframe[1][3]
        self._errors[caller_name] = error

    def add_version(self, description: str, version: int, caller_name: str):
        if not self._is_running:
            return
        self._versions[description][caller_name] = version

    def add_exception(self, exception: Exception):
        if not self._is_running:
            return
        self._exceptions.append(exception)

    def add_updating_status(
        self, description: str, is_updating: bool, caller_name: str
    ):
        if not self._is_running:
            return
        self._updating_statuses[description][caller_name] = is_updating

    @property
    def is_running(self):
        return self._is_running

    def __enter__(self):
        self.start()

    def __exit__(self, *args, **kwargs):
        self.stop()

    async def __aenter__(self):
        self.start()

    async def __aexit__(self, *args, **kwargs):
        self.stop()
