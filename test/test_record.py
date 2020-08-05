from collections import OrderedDict

import pytest


def test_basic(record, empty_record):
    assert record.geom is not None
    assert record.bounds is not None
    assert len(record) == 4

    assert empty_record.geom is not None
    assert empty_record.bounds is not None
    assert len(empty_record) == 1


def test_properties(record):
    assert record.id == 1
    assert record.field1 is None
    assert record.field2 == "default"


def test_immutable(record):
    with pytest.raises(AttributeError) as exc:
        record.id = 3

    assert exc.match("can't set attribute")


def test_geo_interface(record):
    gi = record.__geo_interface__

    assert gi.get("type") == "Feature"

    assert gi.get("properties").get("field1") is None
    assert gi.get("properties").get("field2") == "default"

    assert gi.get("geometry").get("type") == "Polygon"
    assert gi.get("geometry").get("coordinates") == (
        ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)),
    )


def test_geojson(record):
    assert record.geojson == {
        "geometry": {
            "coordinates": (
                ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)),
            ),
            "type": "Polygon",
        },
        "properties": OrderedDict([("id", 1), ("field1", None), ("field2", "default")]),
        "type": "Feature",
    }
