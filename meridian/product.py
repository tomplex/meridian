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


def product(
    d1: Dataset[_T], d2: Dataset[_U], predicate: str = "intersects"
) -> Iterator[Tuple[_T, _U]]:
    """
    product returns an iterator of Record tuples which fulfill the chosen predicate.
    Behavior is similar to itertools.product, except that it is not a full cartestian product;
    The tuples first item will match the first Dataset's Record type, and the second will
    match the second.

    the outer loop's geometry is prepared so predicates will be efficient.

    """
    if predicate not in _allowed_prepared_predicates:
        raise ValueError(
            f"Predicate must be one of {','.join(_allowed_prepared_predicates)}"
        )

    for r1 in d1:
        records = d2.intersection(r1)
        if not records:
            continue

        prepped = prep(r1)
        for r2 in records:
            if getattr(prepped, predicate)(r2):
                yield r1, r2


def intersection(d1: Dataset[_T], d2: Dataset[_U]) -> Iterator[Tuple[_T, _U]]:
    """
    A special case of `product` based on the "intersects" predicate.

    """
    yield from product(d1, d2, predicate="intersects")
