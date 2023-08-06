from enum import Enum


class DurationLimit(Enum):
    """DurationLimit enum"""
    SECOND = 7
    MINUTE = 6
    HOUR = 5
    DAY = 4
    WEEK = 3
    MONTH = 2
    YEAR = 1
