import sys
from loguru import logger

from ..timer import Timer


colors = {
    "INFO": "<fg #22a022>",
    "DEBUG": "<magenta>",
    "WARNING": "<yellow>",
    "ERROR": "<red>",
    "CRITICAL": "<red>",
}


class Formatter:
    def __init__(self):
        self.padding = 55
        self.fmt = (
            "<fg #319a9b>[{extra[time]}]</fg #319a9b> "
            "<fg #FFFFBF>{file}:{line}</fg #FFFFBF> "
            "<b><level>{extra[name]} {level}</level></b>{extra[padding]} "
            "{message}\n"
        )

    def format(self, record):
        length = len(
            "{extra[time]} {file}:{line} {extra[name]} {level}".format(**record)
        )
        self.padding = max(self.padding, length)
        record["extra"]["padding"] = " " * (self.padding - length)
        return self.fmt


class Logger:
    def __init__(
        self,
        name: str,
        timer: Timer,
        level: str = "INFO",
    ):
        self.name = name
        self._timer = timer
        logger.remove()
        for lvl, c in colors.items():
            logger.level(lvl, color=c, icon="@")

        formatter = Formatter()
        logger.add(sys.stdout, format=formatter.format, level=level)
        self.logger = logger.bind(name=name)
        self.logger = self.logger.patch(
            lambda record: record["extra"].update(
                time=self._timer.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception
