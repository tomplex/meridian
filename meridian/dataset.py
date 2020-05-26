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
import functools
import itertools
import pickle
import typing

from typing import Tuple, TypeVar, Generic, Iterator

import rtree

from meridian.record import Record


T = TypeVar("T", bound=Record)


class FastRTree(rtree.Rtree):
    def dumps(self, obj):
        return pickle.dumps(obj, -1)


def _check_bounds(query):
    if not hasattr(query, "bounds"):
        raise AttributeError(
            "Query argument to must "
            "implement bounds property returning "
            "(xmin, ymin, xmax, ymax)"
        )


class Dataset(Generic[T]):
    """
    The SpatialDataset is the core piece of meridian.
    It wraps spatial data and exposes methods to manage it.

    """

    def __init__(
        self,
        data: typing.Union[typing.Sequence, typing.Iterable],
        properties: rtree.index.Property = None,
    ):
        """

        Args:
            data:
            properties:
        """
        if hasattr(data, "__next__"):
            # It's an iterator
            first = next(data)
            # reconstruct our initial iterator by chaining
            # the first item with the rest of the iterator
            data = itertools.chain([first], data)
        else:
            # it's a sequence
            first = data[0]

        if not isinstance(first, Record):
            raise TypeError("Input must be an iterable of SpatialData objects")

        self.__data = tuple(data)

        if properties is None:
            properties = rtree.index.Property()
            properties.dimension = 2
            properties.fill_factor = 0.999
            properties.leaf_capacity = 1000

        gen = ((idx, sd.bounds, None) for idx, sd in enumerate(self.__data))
        self.__rtree = FastRTree(gen, properties=properties)

    def __len__(self):
        return len(self.__data)

    def __iter__(self) -> Iterator[T]:
        return iter(self.__data)

    def __getitem__(self, item: int) -> T:
        return self.__data[item]

    @property
    def bounds(self):
        """
        The bounds of the SpatialDataset.

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
        return self.__rtree.count(query.bounds)

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
