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
    left: Dataset[_T], right: Dataset[_U], predicate: str = "intersects"
) -> Iterator[Tuple[_T, _U]]:
    """
    product is returns an iterator of SpatialData tuples which fulfill the chosen predicate.
    Behavior is similar to itertools.product, except that it is not a full cartestian product;
    The tuples first item will match the "left" SpatialDataset's type, and the second will
    match the right.

    the outer loop's geometry is prepared so predicates will be efficient.

    Args:
        left:
        right:
        predicate:

    Returns:

    """
    if predicate not in _allowed_prepared_predicates:
        raise ValueError(
            f"Predicate must be one of {','.join(_allowed_prepared_predicates)}"
        )

    for r1 in left:
        records = right.intersection(r1)
        if not records:
            continue

        prepped = prep(r1)
        for r2 in records:
            if getattr(prepped, predicate)(r2):
                yield r1, r2


def intersection(left: Dataset[_T], right: Dataset[_U]) -> Iterator[Tuple[_T, _U]]:
    """

    Args:
        left:
        right:

    Returns:

    """
    yield from product(left, right, predicate="intersects")
