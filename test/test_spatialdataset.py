
from test.conftest import make_point


def test_intersects(spatial_dataset):
    pt = make_point(0.5, 0.5, as_geom=True)

    assert spatial_dataset.intersects(pt)


def test_count(spatial_dataset):
    pt = make_point(0.5, 0.5, as_geom=True)

    assert spatial_dataset.count(pt) == 1


def test_nearest(spatial_dataset):
    pt = make_point(0.5, 0.5, as_geom=True)
    near = spatial_dataset.nearest(pt)

    assert near[0].id == 1


def test_intersection(spatial_dataset):
    pt = make_point(1, 1, as_geom=True)
    records = spatial_dataset.intersection(pt)

    assert len(records) == 4


def test_bounds(spatial_dataset):
    assert spatial_dataset.bounds == [0.0, 0.0, 2.0, 2.0]


def test_len(spatial_dataset):
    assert len(spatial_dataset) == 4


def test_iter(spatial_dataset):
    iterator = iter(spatial_dataset)
    i = 0
    for _ in iterator:
        i += 1

    assert i == len(spatial_dataset)

