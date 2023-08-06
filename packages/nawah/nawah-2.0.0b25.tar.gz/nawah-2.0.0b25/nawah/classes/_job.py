"""Provides 'Job' dataclass"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from croniter import croniter

    from nawah.types import NawahSession


@dataclass(kw_only=True)
class Job:
    """Job dataclass serves role of defining items of 'jobs' Config Attr which
    are callabled, called periodically per cron-based schedule"""

    job: "JobCallable"
    schedule: str
    prevent_disable: bool

    @property
    def cron_schedule(self) -> "croniter":
        """Getter for '_cron_schedule' attr"""
        return self._cron_schedule

    @cron_schedule.setter
    def cron_schedule(self, val: "croniter"):
        """Setter for '_cron_schedule' attr"""
        self._cron_schedule = val

    @property
    def next_time(self) -> str:
        """Getter for '_next_time' attr"""
        return self._next_time

    @next_time.setter
    def next_time(self, val: str):
        """Setter for '_next_time' attr"""
        self._next_time = val

    @property
    def disabled(self) -> bool:
        """Getter for '_disabled' attr"""
        return self._disabled

    @disabled.setter
    def disabled(self, val: bool):
        """Setter for '_disabled' attr"""
        self._disabled = val

    def __post_init__(self):
        self._cron_schedule = None
        self._next_time = None
        self._disabled = False


class JobCallable(Protocol):
    """Provides type-hint for 'job' callable of 'Job'"""

    # pylint: disable=too-few-public-methods
    def __call__(
        self,
        session: "NawahSession",
    ) -> None:
        ...
