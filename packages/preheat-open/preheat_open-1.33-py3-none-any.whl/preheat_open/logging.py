import inspect
import logging
import sys
import warnings
from typing import Optional, Union

from .singleton import Singleton

LOG_FORMAT = "%(asctime)-23s  %(levelname)-8s  %(name)-32s  %(message)-160s  .(%(filename)s:%(lineno)d)"


class Logging(metaclass=Singleton):
    def __init__(self, stacklevel: int = 0):

        # Ensure the routing of warnings to the logger when using the logger
        logging.captureWarnings(True)

        self.get_root_logger = logging.getLogger
        if sys.gettrace() is None:
            logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        else:
            logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    def _get_logger(self, failsafe: bool = True, stack_level: int = 0):
        try:
            frame = inspect.stack()[2 + stack_level]
            mod = inspect.getmodule(frame[0])
            # return self.get_root_logger(mod.__package__)
            return self.get_root_logger().getChild(mod.__name__.split(".")[-1])
        except Exception as e:
            if failsafe is True:
                warnings.warn(
                    "There was an issue in accessing the desired logger - defaulting to a failsafe one"
                )
                return self.get_root_logger().getChild("Failsafe-log (preheat_open)")
            else:
                raise e

    def set_root_logger(self, func):
        self.get_root_logger = func

    def set_level(self, level: Union[str, int]) -> None:
        logging.basicConfig(level=level, force=True)

    def critical(
        self,
        msg: str,
        exception: Optional[Exception] = None,
        stack_level: int = 0,
        *args,
        **kwargs,
    ) -> None:
        if exception is None:
            for line in str(msg).split("\n"):
                self._get_logger(stack_level=stack_level).critical(
                    line, stacklevel=2 + stack_level, *args, **kwargs
                )
        else:
            try:
                raise exception
            except Exception as e:
                for line in str(msg).split("\n"):
                    self._get_logger(stack_level=stack_level).exception(
                        line, stacklevel=2 + stack_level, *args, **kwargs
                    )

    def error(
        self,
        msg: str,
        exception: Optional[Exception] = None,
        stack_level: int = 0,
        *args,
        **kwargs,
    ) -> None:
        if exception is None:
            for line in str(msg).split("\n"):
                self._get_logger(stack_level=stack_level).error(
                    line, stacklevel=2 + stack_level, *args, **kwargs
                )
        else:
            try:
                raise exception
            except Exception as e:
                for line in str(msg).split("\n"):
                    self._get_logger(stack_level=stack_level).exception(
                        line, stacklevel=2 + stack_level, *args, **kwargs
                    )

    def warning(
        self, msg: Union[str, Warning], stack_level: int = 0, *args, **kwargs
    ) -> None:
        if isinstance(msg, Warning):
            warnings.warn(msg)
        else:
            for line in str(msg).split("\n"):
                self._get_logger(stack_level=stack_level).warning(
                    line, stacklevel=2 + stack_level, *args, **kwargs
                )

    def info(self, msg: str, stack_level: int = 0, *args, **kwargs) -> None:
        for line in str(msg).split("\n"):
            self._get_logger(stack_level=stack_level).info(
                line, stacklevel=2 + stack_level, *args, **kwargs
            )

    def debug(self, msg: str, stack_level: int = 0, *args, **kwargs) -> None:
        for line in str(msg).split("\n"):
            self._get_logger(stack_level=stack_level).debug(
                line, stacklevel=2 + stack_level, *args, **kwargs
            )


def logging_level(level: str) -> int:
    """
    Converts a string to a logging level

    :param level: logging level (debug, info, warning, error, critical)
    :type level:
    :return: logging level identifier (in logging package)
    :rtype:
    """
    if isinstance(level, str):
        str_level = level.lower()
        if str_level == "debug":
            log_level = logging.DEBUG
        elif str_level == "info":
            log_level = logging.INFO
        elif str_level == "warning":
            log_level = logging.WARNING
        elif str_level == "error":
            log_level = logging.ERROR
        elif str_level == "critical":
            log_level = logging.CRITICAL
        else:
            raise Exception(f"Illegal logging level ({level})")

        return log_level

    else:
        raise Exception("Only logging levels in string format are supported for now")


def set_logging_level(level: str) -> None:
    """
    Sets the logging level

    :param level: logging level (debug, info, warning, error, critical)
    :type level:
    """
    Logging().set_level(logging_level(level))
