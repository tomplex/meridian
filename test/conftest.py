

import pytest

from meridian import SpatialDataset
from meridian.spatialdata import _get_spatialdata_factory

from shapely import geometry


_test_spatialdata = _get_spatialdata_factory({
    'id': 0,
    'geometry': {},
    'properties': {
        'field1': 'value1',
        'field2': 'value2'
    }
})


def make_spatialdata(geojson_geometry, feature_id=1, field1=None, field2=None):
    """
    Helper to create a spatialdata object given a geojson geometry and some other attributes.

    """
    return _test_spatialdata({
        'id': feature_id,
        'geometry': geojson_geometry,
        'properties': {
            'field1': field1,
            'field2': field2
        }
    }, 0)


def make_square(xmin=0, ymin=0, delta=1, as_geom=False):
    """
    Make a GeoJSON square.

    if as_geom, then return a shapely geometry instead.

    """
    geojson = {
        'type': 'Polygon',
        'coordinates': [
            [
                [xmin, ymin], [xmin + delta, ymin], [xmin + delta, ymin + delta], [xmin, ymin + delta], [xmin, ymin]
            ]
        ]
    }
    return geometry.shape(geojson) if as_geom else geojson


def make_point(x, y, as_geom=False):
    """
    Make a GeoJSON point.

    if as_geom, then return a shapely geometry instead.

    """
    geojson = {
        'type': 'Point',
        'coordinates': [x, y]
    }
    return geometry.shape(geojson) if as_geom else geojson


@pytest.fixture()
def spatial_dataset():
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

            records.append({
                'type': 'Feature',
                'geometry': make_square(x, y),
                'id': i,
                'properties': {
                    'field1': None,
                    'field2': None
                }
            })

    return SpatialDataset(records)


@pytest.fixture()
def spatialdata():
    return make_spatialdata(
                geojson_geometry=make_square(0, 0),
                feature_id=1,
    )
