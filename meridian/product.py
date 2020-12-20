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
from typing import Iterator, Tuple, TypeVar

from shapely.prepared import prep

from meridian import Dataset, Record

_T = TypeVar("_T", bound=Record)
_U = TypeVar("_U", bound=Record)

_allowed_prepared_predicates = (
    "intersects",
    "contains",
    "contains_properly",
    "covers",
    "crosses",
    "disjoint",
    "overlaps",
    "touches",
    "within",
)


def _error_callback(error: Exception, record: Record) -> dict:
    return {
        'error': str(error),
        'record': record.geojson
    }


class Product:
    """
    Product represents a "spatial join" between two Datasets. It wraps an iterator of Record
    tuples which fulfill the chosen predicate.

    Behavior is similar to itertools.product, except that it is not a full cartestian product;
    The tuples first item will match the first Dataset's Record type, and the second will
    match the second.

    the outer loop's geometry is prepared so predicates will be efficient.
    """
    def __init__(self, d1: Dataset[_T], d2: Dataset[_U], predicate="intersects", error_callback=None) -> None:
        if predicate not in _allowed_prepared_predicates:
            raise ValueError(
                f"Predicate must be one of {','.join(_allowed_prepared_predicates)}"
            )

        self._d1 = d1
        self._d2 = d2
        self._predicate = predicate
        self._errors = []
        self._total_processed = None
        self._error_callback = error_callback or _error_callback

    def __iter__(self):
        for idx, r1 in enumerate(self._d1):
            records = self._d2.intersection(r1)
            if not records:
                continue

            prepped = prep(r1)
            for r2 in records:
                try:
                    if getattr(prepped, self._predicate)(r2):
                        yield r1, r2
                except Exception as e:
                    self._errors.append(self._error_callback(e, r2))

        self._total_processed = idx

    def __len__(self) -> int:
        if self._total_processed is None:
            raise TypeError("Product has no len before it has been run.")
        return self._total_processed

    @property
    def errors(self):
        return self._errors


def product(d1: Dataset[_T], d2: Dataset[_U], predicate: str = "intersects") -> Iterator[Tuple[_T, _U]]:
    """
    Helper function if you don't care about metadata like errors etc.
    """
    yield from Product(d1, d2, predicate)


def intersection(d1: Dataset[_T], d2: Dataset[_U]) -> Iterator[Tuple[_T, _U]]:
    """
    A special case of `Product` based on the "intersects" predicate.
    """
    yield from Product(d1, d2, predicate="intersects")
