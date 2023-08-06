"""A module for working with statistics time."""


import calendar
from enum import Enum
from typing import Optional, Union
from datetime import datetime, timedelta


class StatPeriod(Enum):
    """A class for storing the statistic time periods."""

    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    NONE = None


class StatDate:
    """
    A class for formatting and calculating the start and end dates of the statistics.
    """

    def __init__(
        self,
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
    ):
        """
        StatDate constructor.

        Args:
            start (optional): Start date for pypi statistics.
                If not set, statistics are collected from the earliest available day.
            end (optional): End date for pypi statistics.
                If not set, statistics are collected until the actual day.
        """

        self._start = StatDate.format_start(start)
        self._end = StatDate.format_end(end)
        assert self._start <= self._end, "start must be before end"

    @property
    def start(self) -> datetime:
        """
        A property for storing the start date.

        Note:
            If not set, statistics are collected from the earliest available day.

        Raises:
            AssertionError: If `start` is before `end`.
        """

        return self._start

    @start.setter
    def start(self, start: Optional[Union[str, datetime]] = None) -> None:
        start = StatDate.format_start(start)
        if self.end and start:
            assert start <= self.end, "start must be before end"
        self._start = start

    @property
    def end(self) -> datetime:
        """
        A property for storing the end date.

        Note:
            If not set, statistics are collected until the actual day.

        Raises:
            AssertionError: If `start` is before `end`.
        """

        return self._end

    @end.setter
    def end(self, end: Optional[Union[str, datetime]] = None) -> None:
        end = StatDate.format_end(end)
        if self.start and end:
            assert self.start <= end, "start must be before end"
        self._end = end

    @staticmethod
    def format_start(start: Optional[Union[str, datetime]] = None) -> datetime:
        """
        A method for formatting the start date.

        Args:
            start (optional): Start date for pypi statistics.

        Note:
            - %Y, for example 2022
                will be formatted to 2022-01-01.
            - %Y-%m, for example 2022-01
                will be formatted to 2022-01-01.
            - %Y-%m-%d, for example 2022-01-01
                will be formatted to 2022-01-01.
            - None
                will be formatted to the earliest available date.

        Returns:
            The formatted start date object.

        Raises:
            ValueError: If `start` can not be formatted.
        """

        time_delta_max = 181
        if start is None:
            time_delta = timedelta(days=time_delta_max)
            start = datetime.now() - time_delta
        if isinstance(start, datetime):
            start = start.strftime("%Y-%m-%d")
        parsed_start = start.split("-")
        if len(parsed_start) == 1:
            start += "-01-01"
        elif len(parsed_start) == 2:
            start += "-01"
        elif len(parsed_start) == 3:
            pass
        else:
            raise ValueError(f"{start} format is incorrect")
        return datetime.strptime(start, "%Y-%m-%d")

    @staticmethod
    def format_end(end: Optional[Union[str, datetime]] = None) -> datetime:
        """
        A method for formatting the end date.

        Args:
            end (optional): End date for pypi statistics.

        Note:
            - %Y, for example 2022
                will be formatted to 2022-12-31.
            - %Y-%m, for example 2022-12
                will be formatted to 2022-12-31.
            - %Y-%m-%d, for example 2022-12-31
                will be formatted to 2022-12-31.
            - None
                will be formatted to the actual date.

        Returns:
            The formatted end date object.

        Raises:
            ValueError: If `end` can not be formatted.
        """

        if end is None:
            end = datetime.now()
        if isinstance(end, datetime):
            end = end.strftime("%Y-%m-%d")
        parsed_end = end.split("-")
        if len(parsed_end) == 1:
            end += "-12-31"
        elif len(parsed_end) == 2:
            end += "-" + str(
                calendar.monthrange(int(parsed_end[0]), int(parsed_end[1]))[1]
            )
        elif len(parsed_end) == 3:
            pass
        else:
            raise ValueError(f"{end} format is incorrect")
        return datetime.strptime(end, "%Y-%m-%d")
