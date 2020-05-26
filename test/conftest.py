import typing

import pytest

from shapely.geometry import shape

from meridian import Dataset, Record


from shapely import geometry


class TestRecord(Record):
    id: int
    field1: str
    field2: str = 'default'


class EmptyRecord(Record):
    pass


def make_testrecord(geojson_geometry, feature_id=1, field1=None, field2=None):
    """
    Helper to create a spatialdata object given a geojson geometry and some other attributes.

    """
    return TestRecord(shape(geojson_geometry), id=feature_id, field1=field1, field2=field2)


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
    return make_testrecord(geojson_geometry=make_square(0, 0), feature_id=1)


@pytest.fixture()
def empty_record():
    return EmptyRecord.from_geojson({
        'geometry': make_point(0, 0),
        'properties': {}
    })
