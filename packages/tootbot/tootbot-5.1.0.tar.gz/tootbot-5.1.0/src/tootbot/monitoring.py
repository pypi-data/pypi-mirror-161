"""Classes / Methods to assist with monitoring continued operation of
tootboot."""
from typing import Optional
from typing import TypeVar

import httpx

from .control import Configuration

HC = TypeVar("HC", bound="HealthChecks")


class HealthChecks:
    """Class to make monitoring the operation of tootboot with Healthchecks
    (healthchecks.io) easier."""

    def __init__(self: HC, config: Configuration) -> None:
        self.base_url = config.health.base_url
        self.uid = config.health.uuid
        self.logger = config.bot.logger

    def check(self: HC, data: str = "", check_type: Optional[str] = None) -> None:
        """Check in with a Healthchecks installation.

        Keyword Arguments:
            data (string):
                Data to send along with the check in. Can be used to include a short
                status along with the check in.
            check_type (string):
                - Type of check in. An empty (None) check_type signals an ok check in
                  and also the successful completion of an earlier 'start' check in
                  type.
                - check_type of 'start' signals the start of a process
                - check_type of 'fail' signals the failure. This can include the
                  failure of an earlier start check in
        """
        url = self.base_url + self.uid
        if check_type is not None:
            url = url + "/" + check_type
        try:
            httpx.post(url=url, content=data, timeout=3).raise_for_status()
            if self.logger is not None:
                check_type = "OK" if check_type is None else check_type
            self.logger.debug("Monitoring ping sent of type: %s", check_type)
        except httpx.HTTPError as requests_exception:
            if self.logger is not None:
                self.logger.error(
                    'During Monitoring "OK Ping" we got: %s', requests_exception
                )

    def check_ok(self: HC, data: str = "") -> None:
        """Convenience method to signal an OK completion of a process."""
        self.check(data=data)

    def check_start(self: HC, data: str = "") -> None:
        """Convenience method to signal the start of a process."""
        self.check(data=data, check_type="start")

    def check_fail(self: HC, data: str = "") -> None:
        """Convenience method to signal the failure of a process."""
        self.check(data=data, check_type="fail")
