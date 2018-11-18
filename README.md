# meridian

Higher-level geospatial data abstractions for Python.


`meridian` lets you treat your geospatial dataset like you would a normal Python data structure, backed by a spatial index for high-performance geospatial queries.


# Usage

The core data structure implemented is the `SpatialDataset`, which takes an iterable (`list`, `generator`, etc) of [GeoJSON](http://geojson.org/)-structured `dict`s and builds up the dataset and index. The records in your dataset are stored within the `SpatialDataset` as `namedtuples` with all the input field names as attributes. Once it's done loading, you have a familiar-feeling data structure you can use to query your dataset.

`meridian` is fully compatible with the GeoJSON-like objects produced by the `fiona` library, which makes it very easy to use:

```python
import fiona

from meridian import SpatialDataset
from shapely import geometry

with fiona.open('/path/to/my/shapefile.shp') as src:
    dataset = SpatialDataset(src)
    

poi = geometry.shape({
    'type': 'Point',
    'coordinates': [-72.319261, 43.648956]
})

for record in dataset.intersection(poi):
    print(record)

```

All of the spatial query methods on a `SpatialDataset` require only that the query object has a `bounds` property which returns a 4-tuple like `(xmin, ymin, xmax, ymax)`. As long as that exists, `meridian` is agnostic of query geometry implementation, however it does use `shapely` geometry on the backend for the records stored within.

The records in a `SpatialDataset` are `spatialdata` `namedtuples` with three special properties:

```python

for record in dataset:
    print(record.id)  # The id in the `id` field of the input geojson
    print(record.geom)  # The `shapely` geometry representation of the record
    print(record.bounds)  # The bounds of the geometry
    print(record.my_fancy_property)  # All other properties in the geojson feature will be exposed as attributes on the namedtuple
```

Since the `id` field is not part of the GeoJSON spec it is optional to include; the library will function just fine without it. However, it does give the user a means to uniquely identify the records within each dataset.


# Installation

`meridian` requires GEOS (for the `shapely` library) and [`libspatialindex`](https://libspatialindex.github.io/) to create the spatial index used for querying. On most systems, `libspatialindex` must be compiled from source. These instructions should work on Linux & macOS:

```bash
wget -qO- http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz | tar xz -C /tmp
cd /tmp/spatialindex-src-1.8.5 && ./configure; make; make install
```

On Linux, you might be to run `ldconfig` afterwards to ensure that the `rtree` python library can find the library correctly.

# Gotcha's

Data takes up memory. Depending on the number & size of the geometries you're trying to work with, you might run out of memory. On my machine, a 2016 MacBook Pro, I found that a dataset with 350k records with an average of 6 nodes per polygon used ~500mb of memory footprint. YMMV. 

`meridian` is opinionated and believes that data should be immutable. If you need your data to change, you should create new data representing your input + processing instead of changing old data. Thus, a `SpatialDataset` is more like a `frozenset` in behavior than a `list`. 


# Planned features

- Format compat. Built-in tools to help load data from other formats (Postgres, WKT, etc)
- Helper function for common geospatial comparisons between `spatialdata` objects
    