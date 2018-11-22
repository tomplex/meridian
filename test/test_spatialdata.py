from test.conftest import make_point


def test_properties(spatialdata):
    assert spatialdata.field1 is None
    assert spatialdata.field2 is None


def test_geo_interface(spatialdata):
    gi = spatialdata.__geo_interface__

    assert gi.get('type') == 'Feature'

    assert gi.get('properties').get('field1') is None
    assert gi.get('properties').get('field2') is None

    assert gi.get('geometry').get('type') == 'Polygon'
    assert gi.get('geometry').get('coordinates') == (((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)),)


def test_intersects(spatialdata):
    pt = make_point(0.5, 0.5, as_geom=True)
    assert spatialdata.intersects(pt)
    assert pt.intersects(spatialdata)


def test_within(spatialdata):
    pt = make_point(0.5, 0.5, as_geom=True)
    assert not spatialdata.within(pt)
    assert pt.within(spatialdata)


def test_contains(spatialdata):
    pt = make_point(0.5, 0.5, as_geom=True)
    assert spatialdata.contains(pt)
    assert not pt.contains(spatialdata)


