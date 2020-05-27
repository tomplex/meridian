from test.conftest import make_point


def test_intersects(dataset):
    pt = make_point(0.5, 0.5, as_geom=True)

    assert dataset.intersects(pt)


def test_count(dataset):
    pt = make_point(0.5, 0.5, as_geom=True)

    assert dataset.count(pt) == 1


def test_nearest(dataset):
    pt = make_point(0.5, 0.5, as_geom=True)
    near = dataset.nearest(pt)

    assert near[0].id == 1


def test_intersection(dataset):
    pt = make_point(1, 1, as_geom=True)
    records = dataset.intersection(pt)

    assert len(records) == 4


def test_bounds(dataset):
    assert dataset.bounds == [0.0, 0.0, 2.0, 2.0]


def test_len(dataset):
    assert len(dataset) == 4


def test_iter(dataset):
    iterator = iter(dataset)
    i = 0
    for _ in iterator:
        i += 1

    assert i == len(dataset)
