# meridian

[![PyPI version](https://badge.fury.io/py/meridian.svg)](https://badge.fury.io/py/meridian)

Performant geospatial data processing in Python's language.

Meridian lets you treat your geospatial dataset like you would a normal Python data structure, backed with a 
spatial index for high-performance geospatial queries. All data is stored in tuple-like objects, which makes it 
very memory-efficient. A dataset opened with Meridian can use up to half as much memory as the same 
dataset in GeoPandas, depending on the characteristics of the geometry. 

### Note: this library is still in alpha. The API and functionality will change often and without notice.

## Design goals

Geospatial data and processes which deal with it have a rather significant bit of jargon associated with them, and that
jargon is heavily influenced by the relational database environment in which many people manipulate spatial data. When
you try to describe to someone the process by which you relate one dataset to another, matching records from each
where geometries intersect, the word that naturally comes to mind is a *spatial join*. This terminology is even present 
in most desktop GIS applications, making it a very common mental model for processing these kids of data.

Often times, I find that tools and libraries try to make Python fit into the world of spatial joins and relational 
databases, and while there have been several *very* successful projects to do so, it has never felt right to me. 
Something has always been lost in translation and I don't feel like I'm writing idiomatic Python code. Besides, "JOIN"
is basically just syntacic sugar for a nested for loop:

```postgresql
select 
    *
from table1
left join table2 on st_intersects(table2.geom, table2.geom)
```

is approximately equivalent to

```python
for r1 in table1:
    for r2 in table2:
        if intersects(r1, r2):
            # do something
```

Iteration is already a core part of Python which is highly optimized, can be done lazily (with generators), has many 
libraries built around manipulating it (like `itertools`) and is well known to users of Python, so why do we need 
JOIN syntax at all?

Meridian, at its core, is trying to make bring these concepts for geospatial data processing into common Python idioms, 
so you can use familiar terminologies, tools, and mental models when you're dealing with it.

Meridian is not trying to displace a tool like Geopandas, which is excellent for exploring and understanding datasets.
Instead, Meridian wants to be an efficient option for intensive and repeated geospatial processing applications
once data exploration is concluded.

Some items which are important to me, in no particular order:
 - Pythonic. should be interoperable with standard library tools and be intuitive to use.
 - Efficient. Memory use is kept as low as possible and operations are optimized when appropriate.
 - Typed wherever possible.
 - Strong support for dataset attribution.


Meridian's `Record` models draw strong inspiration from `pydantic`'s `BaseModel`, choosing to re-invent a small
part of that wheel for the purpose of efficiency and narrowing of focus.


## Usage

### When shouldn't I use Meridian?

Meridian is not meant to be a replacement for a database system, and as such it's not particularly 
optimized or ergonomic for operations like finding specific records, though this is pretty easy to 
do with a filter. Also, if your data is highly mutable, e.g. you want to modify records in place, then
you should probably look elsewhere.

---

### When should I use Meridian?

Meridian shines when you have some reference dataset that you want to compare to an input dataset or single record.

Meridian expects that you have a decent understanding of the data which you would like to work with. It requires
you to define an annotated model class which lists the attributes of the dataset which you want to work with. 
You do this by subclassing the `meridian.Record` object:

```python
import meridian

class County(meridian.Record):
    name: str
    fips: str
    
``` 

Supposing you had a shape file with county geometry and the fields above, you could create a `Dataset`
of `County`s like so:

```python
counties = County.load_from("path/to/counties.shp")
```

Meridian depends on the Fiona library to open most data files, which requires GDAL/OGR. 
Wheels are available for many platforms, but not all.

Creating a `Dataset` will immediately load the data into memory and create a spatial index
which will be used for all queries. A `Dataset` has many attributes of other Python data structures:
it is iterable, has a `len`, etc.


```python
import meridian

from shapely import geometry


class County(meridian.Record):
    name: str
    fips: str

counties = County.load_from("path/to/counties.shp")

# Find out how many records you have
print(len(counties))

poi = geometry.shape({
    'type': 'Point',
    'coordinates': [-72.319261, 43.648956]
})

# Check if your poi intersects with the dataset
print(counties.intersects(poi)) # True

# See how many records intersect
print(counties.count(poi)) # 1

# Find the n nearest records to the query geometry
print(counties.nearest(poi, 3))

# The dataset itself is iterable.
for county in counties:
    print(county.name)

# iterate through all records in the dataset which bbox-intersect with poi
# Dataset.intersection returns a tuple of Records.
for county in counties.intersection(poi):
    print(county.name)

```

Please note that spatial methods check only for a bounding-box intersection; you must confirm that the 
objects returned actually intersect with your input. 

All of the spatial query methods on a `Dataset` require only that the query object has a `bounds` 
property which returns a 4-tuple like `(xmin, ymin, xmax, ymax)`. As long as that exists, 
`meridian` is agnostic of query geometry implementation, however it does use `shapely` geometry 
under the hood for the records stored within.

```python
poi = geometry.shape({
    'type': 'Point',
    'coordinates': [-72.319261, 43.648956]
})

for county in counties:
    print(county.geojson)  # get back the record as GeoJSON
    print(county.bounds)  # The bounds of the geometry
    print(county.name) 
    
    # Record objects are fully compatible with all of the
    # objects & operations defined in the shapely package.
    print(poi.intersects(county))


# Even advanced operations like cascaded union work as expected.
from shapely.ops import cascaded_union

subset = counties.intersection(poi)

unioned = cascaded_union(subset)
print(unioned.wkt)

```

Finally, Meridian also includes utilities to easily and efficiently relate multiple datasets.

For now, see the `examples` directory.

TO BE FILLED IN:
 - Product / intersection helpers
 - Model behavior
    - Field defaults
    - Derived attributes


# Installation

`meridian` requires GEOS (for the `shapely` library) and [`libspatialindex`](https://libspatialindex.github.io/) to create the spatial index used for querying. On most systems, `libspatialindex` must be compiled from source. These instructions should work on Linux & macOS:

```bash
wget -qO- http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz | tar xz -C /tmp
cd /tmp/spatialindex-src-1.8.5 && ./configure; make; make install
```

On Linux, you might need to run `ldconfig` afterwards to ensure that the `rtree` python library can find the library correctly.

From `pypi`:

    pip install meridian

Or, clone the repo and run

    python path/to/repo/setup.py install

You can also use `pip` to install directly from the github repo:

    pip install git+git://github.com/tomplex/meridian.git

If you use docker, there are images with all dependencies and the latest version of `meridian` pre-installed available on [docker hub](https://hub.docker.com/r/tomplex/meridian-base/).

# Opinions

`meridian` is opinionated and believes that data should generally be immutable. If you need your data to change, you should create new data representing your input + processing instead of changing old data. Thus, a `Dataset` is more like a `frozenset` in behavior than a `list`. 
