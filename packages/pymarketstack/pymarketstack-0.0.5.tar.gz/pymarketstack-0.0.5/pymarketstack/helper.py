"""
Contains helper functions for pymarketstack, not intended for public use.
"""

from typing import List, Generator


def chunk(stocks: List[str], size: int) -> Generator[List[str], None, None]:
    """
    Yields chunks from the input list where each chunk is `size` large.

    :param stocks: The input
    :param size: The size of each chunk
    :return: A generator that yields each chunk
    """

    for i in range(0, len(stocks), size):
        yield stocks[i:i + size]
