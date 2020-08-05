import pytest

from shapely import geometry

from meridian import Dataset, Record


class TestRecord(Record):
    id: int
    field1: str
    field2: str = "default"


class EmptyRecord(Record):
    pass


def make_square(xmin=0, ymin=0, delta=1, as_geom=False):
    """
    Make a GeoJSON square.

    if as_geom, then return a shapely geometry instead.

    """
    geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [xmin, ymin],
                [xmin + delta, ymin],
                [xmin + delta, ymin + delta],
                [xmin, ymin + delta],
                [xmin, ymin],
            ]
        ],
    }
    return geometry.shape(geojson) if as_geom else geojson


def make_point(x, y, as_geom=False):
    """
    Make a GeoJSON point.

    if as_geom, then return a shapely geometry instead.

    """
    geojson = {"type": "Point", "coordinates": [x, y]}
    return geometry.shape(geojson) if as_geom else geojson


@pytest.fixture()
def dataset():
    """
    Fixture to build up a spatialdataset with four polygons, like so:

     --------
    | 2 | 4 |
     --------
    | 1 | 3 |
     --------

    Returns:

    """
    records = []
    i = 0
    for x in range(0, 2):
        for y in range(0, 2):
            i += 1

            records.append(
                TestRecord.from_geojson(
                    {
                        "type": "Feature",
                        "geometry": make_square(x, y),
                        "properties": {"field1": None, "field2": None, "id": i},
                    }
                )
            )

    return Dataset(records)


@pytest.fixture()
def record():
    return TestRecord.from_geojson(
        {"geometry": make_square(0, 0), "properties": {"id": 1, "field1": None}}
    )


@pytest.fixture()
def empty_record():
    return EmptyRecord.from_geojson({"geometry": make_point(0, 0), "properties": {}})
