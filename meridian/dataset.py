# Copyright (c) 2019 Tom Caruso & individual contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import itertools
import pickle
import typing

from typing import Tuple, TypeVar, Generic, Iterator

import rtree

from meridian.record import Record


T = TypeVar("T", bound=Record)


class FastRTree(rtree.Rtree):
    """A faster Rtree which uses a lower protocol when pickling objects for storage."""

    def dumps(self, obj):
        return pickle.dumps(obj, -1)


def _check_bounds(query: typing.Any):
    """Ensure the input object has a `bounds` attribute."""
    if not hasattr(query, "bounds"):
        raise AttributeError(
            "Query argument to must "
            "implement bounds property returning "
            "(xmin, ymin, xmax, ymax)"
        )


class Dataset(Generic[T]):
    """
    The Dataset provides a wrapper for Records, giving the user a way to query
    the Records within spatially.
    """

    def __init__(
        self, data: typing.Iterator[T], properties: rtree.index.Property = None,
    ):
        if not hasattr(data, "__next__"):
            data = iter(data)

        peek = next(data)

        if not isinstance(peek, Record):
            raise TypeError("Input must be an iterable of SpatialData objects")

        self.__data = tuple(itertools.chain([peek], data))

        if properties is None:
            properties = rtree.index.Property()
            properties.dimension = 2
            properties.fill_factor = 0.999
            properties.leaf_capacity = 1000

        gen = ((idx, sd.bounds, None) for idx, sd in enumerate(self.__data))
        self.__rtree = FastRTree(gen, properties=properties)

    def __len__(self) -> int:
        """Number of Records in the Dataset"""
        return len(self.__data)

    def __iter__(self) -> Iterator[T]:
        """Create an iterator over the Records in the dataset."""
        return iter(self.__data)

    def __getitem__(self, item: int) -> T:
        """Get an item from the Dataset by index."""
        return self.__data[item]

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
        The bounds of the Dataset.

        Returns: 4-tuple (xmin, ymin, xmax, ymax)
        """
        return self.__rtree.bounds

    def intersects(self, query) -> bool:
        """
        Check if the SpatialDataset intersects
        with the query object.

        Args:
            query:

        Returns:
            bool

        """
        _check_bounds(query)
        return self.__rtree.count(query.bounds) != 0

    def intersection(self, query) -> Tuple[T, ...]:
        """
        Find the intersection of the input geometry /
        spatial data and the SpatialDataset.

        Args:
            query: an object which exposes a `bounds`
            property of the (xmin, ymin, xmax, ymax) format.

        Returns:
            SpatialDataset of intersecting objects
        """
        _check_bounds(query)
        return tuple(self.__data[i] for i in self.__rtree.intersection(query.bounds))

    def count(self, query) -> int:
        """
        Count the number of objects in the SpatialDataset
        which intersect with the query object.

        Args:
            query: an object which exposes a `bounds`
            property of the (xmin, ymin, xmax, ymax) format.

        Returns:
            int
        """
        _check_bounds(query)
        return int(self.__rtree.count(query.bounds))

    def nearest(self, query, num_results=1) -> Tuple[T, ...]:
        """
        Find the nearest n objects in the
        SpatialDataset to the query object.

        Args:
            query:
            num_results:

        Returns:
            tuple of nearest records
        """
        _check_bounds(query)
        return tuple(self[i] for i in self.__rtree.nearest(query.bounds, num_results))
