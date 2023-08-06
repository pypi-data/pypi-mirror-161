"""

"""

from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json, config
import datetime as dt

from marshmallow import fields


@dataclass_json
@dataclass
class Pagination:
    """The pagination object returned from marketstack's request."""
    limit: int
    offset: int
    count: int
    total: int


@dataclass_json
@dataclass
class Data:
    """The data fields returned from marketstack's request."""
    open: float
    high: float
    low: float
    close: float
    volume: int
    close: int
    adj_high: float | None
    adj_low: float | None
    adj_close: float | None
    adj_volume: float | None
    split_factor: float
    dividend: float
    symbol: str
    exchange: str
    date: dt.datetime = field(
        metadata=config(
            encoder=dt.datetime.isoformat,
            decoder=lambda a: dt.datetime.fromisoformat(a[0:a.find("+")]),
            mm_field=fields.DateTime(format="iso")
        ))


@dataclass_json
@dataclass
class Response:
    """The response object received from marketstack."""
    pagination: Pagination
    data: List[Data]


@dataclass_json
@dataclass
class Error:
    """The response object on failure."""
    code: str
    message: str
