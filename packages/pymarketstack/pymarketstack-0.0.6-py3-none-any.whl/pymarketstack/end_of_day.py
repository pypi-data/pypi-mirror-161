"""
Contains the interface for the End-of-Day data features
"""

from typing import List, Optional
from enum import Enum
import datetime as dt


class Order(Enum):
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class EndOfDay:
    @staticmethod
    def query(
            token: str,
            exchange: Optional[str] = None,
            order: Order = Order.ASCENDING,
            date_from: Optional[dt.datetime.date] = None,
            date_to: Optional[dt.datetime.date] = None,
            offset: int = 0,
            encryption: bool = False) -> str:

        """
        Constructs a query string for the plain eod data feature.

        :param token: The API access key
        :param exchange: [Optional] a market exchange
        :param order: [Optional] the order to present the data in, default is ascending
        :param date_from: [Optional] The first date to receive data from
        :param date_to: [Optional] The last date to receive data from
        :param offset: Offsets the pagination
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

        # If a from-date was specified
        if date_from is not None:
            url = f"{url}&date_from={date_from.strftime('%Y-%m-%d')}"

        # If a to-date was specified
        if date_to is not None:
            url = f"{url}&date_to={date_to.strftime('%Y-%m-%d')}"

        return url

    @staticmethod
    def query_latest(
            token: str,
            exchange: Optional[str] = None,
            encryption: bool = False) -> str:

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

        return url


    @staticmethod
    def query_date(
            token: str,
            date: dt.datetime,
            exchange: Optional[str] = None,
            encryption: bool = False) -> str:

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

        return url
