import datetime as dt
from dataclasses import dataclass


@dataclass
class DateRange:
    start: dt.datetime
    end: dt.datetime

    def days(self):
        return (self.end - self.start).days


@dataclass
class Query:
    url: str
    count: int
