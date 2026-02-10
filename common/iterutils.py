"""Shared iteration utilities using more-itertools.

Provides convenient re-exports of commonly used more-itertools functions
for use across logxpy, logxpy_cli_view, and logxy-log-parser.

Reference: docs/more-itertools-ref.md

Categories:
- Grouping: chunked, batched, ichunked, grouper, bucket
- Lookahead: peekable, seekable
- Iterating: consume, nth, first, last, one
- Filtering: filter_except, map_except, split_at, partition
- Windowing: windowed, sliding_window
"""

from __future__ import annotations

# Grouping functions
from more_itertools import (
    batched,
    bucket,
    chunked,
    ichunked,
)

# Filtering functions
from more_itertools import (
    filter_except as _filter_except,
    map_except as _map_except,
    partition,
    split_at,
)

# Iterating helpers
from more_itertools import (
    consume,
    first as _first,
    last as _last,
    nth,
    one as _one,
)

# Lookahead
from more_itertools import peekable, seekable

# Windowing
from more_itertools import sliding_window, windowed

# Other utilities
from more_itertools import (
    flatten as _flatten,
    grouper as _grouper,
    pairwise,
    unique_everseen,
)

__all__ = [
    # Grouping
    "chunked",
    "batched",
    "ichunked",
    "bucket",
    "grouper",
    # Filtering
    "filter_except",
    "map_except",
    "partition",
    "split_at",
    # Iterating
    "consume",
    "first",
    "last",
    "nth",
    "one",
    # Lookahead
    "peekable",
    "seekable",
    # Windowing
    "windowed",
    "sliding_window",
    # Other
    "flatten",
    "pairwise",
    "unique_everseen",
]


def flatten(iterable, *args, **kwargs):
    """Flatten nested iterables.

    Wrapper around more_itertools.flatten that provides sensible defaults.

    Args:
        iterable: The nested iterable to flatten
        *args, **kwargs: Passed to more_itertools.flatten

    Returns:
        Flattened iterator
    """
    return _flatten(iterable, *args, **kwargs)


def first(iterable, default=None):
    """Return first item of iterable or default.

    Args:
        iterable: Iterable to get first item from
        default: Default value if iterable is empty

    Returns:
        First item or default

    Example:
        >>> first([1, 2, 3])
        1
        >>> first([], default=None)
        None
    """
    return _first(iterable, default=default)


def last(iterable, default=None):
    """Return last item of iterable or default.

    Args:
        iterable: Iterable to get last item from
        default: Default value if iterable is empty

    Returns:
        Last item or default
    """
    return _last(iterable, default=default)


def one(iterable):
    """Return the only item in iterable.

    Raises ValueError if iterable has more than one item.

    Args:
        iterable: Iterable to get item from

    Returns:
        The only item

    Raises:
        ValueError: If iterable doesn't have exactly one item
    """
    return _one(iterable)


def filter_except(func, *exceptions, iterable):
    """Filter yielding items where func() doesn't raise exceptions.

    Args:
        func: Function to apply to each item
        *exceptions: Exception types to catch
        iterable: Iterable to filter

    Yields:
        Items where func(item) didn't raise an exception

    Example:
        >>> filter_except(int, ValueError, ["1", "a", "2"])
        [1, 2]
    """
    return _filter_except(func, exceptions, iterable)


def map_except(func, *exceptions, iterable):
    """Map func over iterable, skipping items where func raises exceptions.

    Args:
        func: Function to apply to each item
        *exceptions: Exception types to catch
        iterable: Iterable to map over

    Yields:
        Results of func(item) where no exception was raised

    Example:
        >>> map_except(int, ValueError, ["1", "a", "2"])
        [1, 2]
    """
    return _map_except(func, exceptions, iterable)


def grouper(iterable, n, fillvalue=None):
    """Group data into fixed-length chunks.

    Args:
        iterable: Iterable to group
        n: Size of each group
        fillvalue: Value to use for last group if incomplete

    Returns:
        Iterator of tuples

    Example:
        >>> list(grouper('ABCDEFG', 3, 'x'))
        [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]
    """
    return _grouper(iterable, n, fillvalue)
