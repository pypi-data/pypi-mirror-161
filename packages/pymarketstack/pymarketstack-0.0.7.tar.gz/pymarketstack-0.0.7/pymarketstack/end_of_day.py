"""
Contains the interface for the End-of-Day data features
"""

from typing import List, Optional
from enum import Enum
from pymarketstack.query import *


class Order(Enum):
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class EndOfDay:
    @staticmethod
    def query(
            token: str,
            exchange: Optional[str] = None,
            order: Order = Order.ASCENDING,
            date_range: Optional[DateRange] = None,
            offset: int = 0,
            count: int = 100,
            encryption: bool = False) -> Query:

        """
        Constructs a query string for the plain eod data feature.

        :param token: The API access key
        :param exchange: [Optional] a market exchange
        :param order: [Optional] the order to present the data in, default is ascending
        :param date_range: [Optional] the range of dates to download
        :param offset: Offsets the pagination
        :param count: The data count per symbol to download, it's overridden if the data_range is specified
        :param encryption: If true, uses HTTPS instead of HTTP, this is an account option.
        :return: A constructed API query string
        """

        # Asserts ranges
        assert offset >= 0

        # Specifies the url and provides the defaulted query options
        url = "{}://api.marketstack.com/v1/eod?access_key={}&sort={}&offset={}".format(
            "https" if encryption else "http",
            token,
            order.value,
            offset
        )

        # If an exchange was specified
        if exchange is not None:
            url = f"{url}&exchange={exchange}"
        
        # If a specific range of dates was specified
        if date_range is not None:
            c = date_range.days()
        else:
            c = count

        return Query(url, c)


    @staticmethod
    def query_latest(
            token: str,
            exchange: Optional[str] = None,
            encryption: bool = False) -> Query:

        """
        Constructs a query string for the eod/latest feature.

        :param token: The API access key
        :param exchange: [Optional] a market exchange
        :param encryption: If true, uses HTTPS instead of HTTP, this is an account option.
        :return: A constructed API query string
        """

        # Specifies the url and provides the defaulted query options
        url = "{}://api.marketstack.com/v1/eod/latest?access_key={}".format(
            "https" if encryption else "http",
            token,
        )

        # If an exchange was specified
        if exchange is not None:
            url = f"{url}&exchange={exchange}"

        return Query(url, 1)


    @staticmethod
    def query_date(
            token: str,
            date: dt.datetime,
            exchange: Optional[str] = None,
            encryption: bool = False) -> Query:

        """
        Constructs a query string for the eod/date feature.

        :param token: The API access key
        :param date: The date to download
        :param exchange: [Optional] a market exchange
        :param encryption: If true, uses HTTPS instead of HTTP, this is an account option.
        :return: A constructed API query string
        """

        url = "{}://api.marketstack.com/v1/eod/{}?access_key={}".format(
            "https" if encryption else "http",
            date.strftime("%Y-%m-%d"),
            token
        )

        if exchange is not None:
            url = f"{url}&exchange={exchange}"

        return Query(url, 1)
