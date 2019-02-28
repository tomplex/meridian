# meridian

[![PyPI version](https://badge.fury.io/py/meridian.svg)](https://badge.fury.io/py/meridian)

Higher-level geospatial data abstractions for Python.


`meridian` lets you treat your geospatial dataset like you would a normal Python data structure, backed by a spatial index for high-performance geospatial queries.


# Usage

The core data structure implemented is the `SpatialDataset`, which takes an iterable (`list`, `generator`, etc) of [GeoJSON](http://geojson.org/)-structured `dict`s and builds up the dataset and index. The records in your dataset are stored within the `SpatialDataset` as `namedtuples` (named `spatialdata`) with all the key/value pairs in the GeoJSON's `properties` as attributes. Once it's done loading, you have a familiar-feeling data structure you can use to query your dataset.

`meridian` is fully compatible with the GeoJSON-like objects produced by the `fiona` library, which makes it very easy to use:

```python
import fiona

from meridian import SpatialDataset
from shapely import geometry

with fiona.open('/path/to/my/shapefile.shp') as src:
    dataset = SpatialDataset(src)

# Find out how many records you have
print(len(dataset))

poi = geometry.shape({
    'type': 'Point',
    'coordinates': [-72.319261, 43.648956]
})

# Check if your poi intersects with the dataset
print(dataset.intersects(poi)) # True

# See how many records intersect
print(dataset.count(poi)) # 1

# Find the n nearest records to the query geometry
print(dataset.nearest(poi, 3))

# The dataset itself is iterable.
for record in dataset:
    print(record)

# iterate through all records in the dataset which bbox-intersect with poi
# dataset.intersection returns a list of spatialdata objects
for record in dataset.intersection(poi):
    print(record)


```

All of the spatial query methods on a `SpatialDataset` require only that the query object has a `bounds` property which returns a 4-tuple like `(xmin, ymin, xmax, ymax)`. As long as that exists, `meridian` is agnostic of query geometry implementation, however it does use `shapely` geometry under the hood for the records stored within.

The records in a `SpatialDataset` are `SpatialData`s:

```python
poi = geometry.shape({
    'type': 'Point',
    'coordinates': [-72.319261, 43.648956]
})

for record in dataset:
    print(record.id)  # The id in the `id` field of the input geojson
    print(record.geom)  # The `shapely` geometry representation of the record
    print(record.bounds)  # The bounds of the geometry
    print(record.properties)  # a dict of all the `properties` in the initial geojson feature
    print(record.my_fancy_property)  # All individual properties in the geojson feature will be exposed as attributes on the namedtuple
    
    # SpatialData objects are fully compatible with all of the objects & operations defined in the shapely package.
    print(record.intersects(poi))
    print(poi.intersects(record))

# Even advanced operations like cascaded union work as expected.
from shapely.ops import cascaded_union

unioned = cascaded_union(dataset)
print(unioned.wkt)

```

Since the `id` field is not part of the GeoJSON spec it is optional to include; the library will function just fine without it. However, it does give the user a means to uniquely identify the records within each dataset.


# Installation

From `pypi`:

    pip install meridian

Or, clone the repo and run

    python path/to/repo/setup.py install

You can also use `pip` to install directly from the github repo:

    pip install git+git://github.com/tomplex/meridian.git


`meridian` requires GEOS (for the `shapely` library) and [`libspatialindex`](https://libspatialindex.github.io/) to create the spatial index used for querying. On most systems, `libspatialindex` must be compiled from source. These instructions should work on Linux & macOS:

```bash
wget -qO- http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz | tar xz -C /tmp
cd /tmp/spatialindex-src-1.8.5 && ./configure; make; make install
```

On Linux, you might be to run `ldconfig` afterwards to ensure that the `rtree` python library can find the library correctly.

If you use docker, there are images with all dependencies and the latest version of `meridian` pre-installed available on [docker hub](https://hub.docker.com/r/tomplex/meridian-base/).

# Gotcha's

Data takes up memory. Depending on the number & size of the geometries you're trying to work with, you might run out of memory. On my machine, a 2016 MacBook Pro, I found that a dataset with 350k records with an average of 6 nodes per polygon used ~500mb of memory footprint. YMMV. 

`meridian` is opinionated and believes that data should be immutable. If you need your data to change, you should create new data representing your input + processing instead of changing old data. Thus, a `SpatialDataset` is more like a `frozenset` in behavior than a `list`. 


# Planned features

- In-depth docs and usage examples
- Format compat. Built-in tools to help load data from other formats (Postgres, WKT, etc)
    
