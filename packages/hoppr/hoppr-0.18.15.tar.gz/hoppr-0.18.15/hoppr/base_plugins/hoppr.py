"""
Base class for all Hoppr plug-ins
"""

import functools
import subprocess
import time
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from packageurl import PackageURL  # type: ignore

from hoppr import plugin_utils
from hoppr.context import Context
from hoppr.mem_logger import MemoryLogger
from hoppr.result import Result
from hoppr.utils import obscure_passwords


def _get_component(*args, **kwargs) -> Optional[Any]:
    # TODO: This will only utilize the first Component found in 1) args, 2) kwargs  # pylint: disable=fixme
    # and assumes all plugins operate this way
    comp = None
    for arg in args:
        if type(arg).__name__ == "Component":
            comp = arg
            break

    if comp is None:
        for value in kwargs.values():
            if type(value).__name__ == "Component":
                comp = value
                break

    return comp


def hoppr_process(func: Callable) -> Callable:
    """
    Decorator to handle generic bookkeeping for hoppr plug-ins
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Result:
        self._start_time = time.time()  # pylint: disable=protected-access
        self.create_logger()

        comp = _get_component(*args, **kwargs)

        arg_string = ""
        if comp is not None:
            arg_string = f"Component purl: {comp.purl}"

        self.get_logger().info(
            f"Starting {self.__class__.__name__}.{func.__name__} {arg_string}"
        )

        result = None
        if comp is not None:
            if comp.purl is None:
                result = Result.fail("No purl supplied for component")

            else:
                purl_type = PackageURL.from_string(comp.purl).type

                if not self.supports_purl_type(purl_type):
                    return Result.skip(
                        f"Class {self.__class__.__name__} does not support purl type {purl_type}"
                    )

                self.get_logger().info(f"Processing purl {comp.purl}")

        if result is None:

            # Only check for missing commands if func has been overridden
            if func.__module__ != HopprPlugin.__module__:
                command_result = plugin_utils.check_for_missing_commands(
                    self.required_commands
                )
                if command_result.is_fail():
                    self.get_logger().error(command_result.message)
                    return command_result

            try:
                result = func(self, *args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                self.get_logger().error(
                    f"Unexpected exception running {self.__class__.__name__}.{func.__name__}: {error}",
                )
                self.get_logger().error(traceback.format_exc())
                result = Result.fail(f"Unexpected Exception: {error}")

        self.get_logger().info(f"Completed {self.__class__.__name__}.{func.__name__}")

        duration = time.time() - self._start_time  # pylint: disable=protected-access
        self.get_logger().info(f"Process duration {duration:3f} seconds")
        self.get_logger().info(f"Result: '{result}'")

        if result.is_skip():
            self.get_logger().clear_targets()

        self.close_logger()

        return result

    return wrapper


def hoppr_rerunner(method: Callable) -> Callable:
    """
    Runs a method (assumed to return a Result object) a number of times,
    or until the result type is not RETRY
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs) -> Result:

        log = self.get_logger()

        for attempt in range(self.context.max_attempts):
            result = method(self, *args, **kwargs)

            if not isinstance(result, Result):
                msg = (
                    f"Method {method.__name__} returned {type(result).__name__}, "
                    + "in rerunner.  Result object required"
                )
                log.error(msg)
                return Result.fail(msg)

            if not result.is_retry():
                return result

            if attempt < self.context.max_attempts - 1:
                log.warning(
                    f"Method {method.__name__} will be retried in "
                    + f"{self.context.retry_wait_seconds} seconds"
                )
                log.warning(
                    f"  Result message for attempt {attempt + 1}: {result.message}"
                )
                time.sleep(self.context.retry_wait_seconds)

        log.error(
            f"Method {method.__name__} failed after {self.context.max_attempts} attempts",
        )
        log.error(f"  Result message for final attempt: {result.message}")

        return Result.fail(
            f"Failure after {self.context.max_attempts} attempts, final message {result.message}"
        )

    return wrapper


class HopprPlugin(ABC):
    """
    Base class for all Hoppr plug-ins

    Note that this class is not thread safe
    """

    required_commands: List[str] = []
    supported_purl_types: List[str] = []

    def __init__(self, context: Context, config: Any = None) -> None:
        self._logger: MemoryLogger
        self._start_time: float = 0.0
        self.context = context
        self.config = config

    @abstractmethod
    def get_version(self) -> str:
        """
        Returns the version of this plug-in
        """

    @hoppr_process
    @hoppr_rerunner
    def pre_stage_process(self) -> Result:
        """
        Process to be run before other processing within a stage for this plug-in
        """

        return Result.skip("pre_stage_process not defined.")

    @hoppr_process
    @hoppr_rerunner
    def process_component(self, comp: Any) -> Result:  # pylint: disable=unused-argument
        """
        Process a single component through this plug-in
        """

        return Result.skip("process_component not defined.")

    @hoppr_process
    @hoppr_rerunner
    def post_stage_process(self):
        """
        Finalize processing for this plug-in
        """
        return Result.skip("post_stage_process not defined.")

    @classmethod
    def supports_purl_type(cls, purl_type: str) -> bool:
        """
        Indicates whether or not this particular plug-in supports components of the specified
        purl type.

        If a plug-in supports all purl types, this method can be overridden to always return True.
        """
        return purl_type in cls.supported_purl_types

    def create_logger(self) -> None:
        """
        Creates a logger with a MemoryHandler, which flushes to stderr when closed
        """

        self._logger = MemoryLogger()

    def get_logger(self) -> MemoryLogger:
        """
        Returns the logger to be used for the current process
        """
        return self._logger

    def close_logger(self) -> None:
        """
        Close (and flush) all handlers for this plug-in's logger
        """
        self._logger.close()

    def run_command(self, command, password_list=None, cwd=None):
        """
        Run a command and log any errors
        """
        result = subprocess.run(command, check=False, capture_output=True, cwd=cwd)
        if result.returncode != 0:
            obscured_command = obscure_passwords(command, password_list)
            self.get_logger().error(f"Failed to execute command: {obscured_command}")
            self.get_logger().info(
                f"PROCESS STDOUT:\n{result.stdout.decode('utf-8').strip()}"
            )
            self.get_logger().info(
                f"PROCESS STDERR:\n{result.stderr.decode('utf-8').strip()}"
            )

        return result
