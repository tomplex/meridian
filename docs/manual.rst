.. _manual:

=======================
Meridian User Manual
=======================


.. _intro:

Introduction
============

Geospatial data and processes which deal with it have a good bit of jargon associated with them, and that
jargon is heavily influenced by the relational database environment in which many people manipulate spatial data. When
you try to describe to someone the process by which you relate one dataset to another, matching records from each
where geometries intersect, the word that naturally comes to mind is a *spatial join*. This terminology is even present
in most desktop GIS applications, making it a very common mental model for processing these kids of data.

Often times, I find that tools and libraries try to make Python fit into the world of spatial joins and relational
databases, and while there have been several *very* successful projects to do so, it has never felt right to me.
Something has always been lost in translation and I don't feel like I'm writing idiomatic Python code. Besides, "JOIN"
is basically just syntacic sugar for a nested for loop:

.. code-block:: sql

    select
      *
    from table1 left join table2
    on st_intersects(table2.geom, table2.geom)

is approximately equivalent to

.. code-block:: python

    for r1 in table1:
        for r2 in table2:
            if intersects(r1, r2):
                # do something


Iteration is already a core part of Python which is highly optimized, can be done lazily (with generators), has many
libraries built around manipulating it (like `itertools`) and is well known to users of Python, so let's talk about these
things in the language of Python, instead of the language of relational databases.

Meridian, at its core, is trying to make bring these concepts for geospatial data processing into common Python idioms,
so you can use familiar terminologies, tools, and mental models when you're dealing with this domain.

Meridian is not trying to displace a tool like Geopandas, which is excellent for exploring and understanding datasets.
Instead, Meridian wants to be an efficient option for intensive and repeated geospatial processing applications
once data exploration is concluded.

.. _core:

Core Models
============

Meridian implements two main data types which users will leverage: the `Record` and the `Dataset`. Naturally, a `Record`
represents an individual row or record in your dataset, while a `Dataset` is a collection of `Record`s with a spatial
index for efficient queries.

Record
^^^^^^^
Create a custom `Record` to model your data by subclassing `meridian.Record` and adding
annotations to the class. The simplest example of which has no annotations and therefore no attributes:

.. code-block:: python

    import meridian

    class GeomOnly(meridian.Record):
        pass

`Record` objects have similar attributes to `NamedTuple`s and `pydantic` models, but "under the hood" they are essentially
`NamedTuples` which always have at least one property called `geom` and implement e.g. the `__geo_interface__` protocol
for compatibility. You can create a `Record` through direct instantiation or the `Record.from_geojson` classmethod:

.. code-block:: python

    from shapely import wkt

    my_geom = wkt.loads("POINT(0 0)")
    empty1 = GeomOnly(my_geom)
    empty2 = GeomOnly.from_geojson({'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {}})

    print(empty1.geom.wkt)
    'POINT(0 0)'

However, in most cases, we will want to define some attributes to go along with our data. We do this by
adding annotations to our class definition:

.. code-block:: python

    import meridian

    class PowerPlant(meridian.Record):
        plant_code: int
        plant_name: str
        sector_name: str
        primsource: str
        install_mw: float
        total_mw: float
        year_built: int = -1

Now, when we create `PowerPlant` objects, each of the annotated attributes will be available as a named property
on the instantiated `Record`. When creating `Record`s, the types of incoming data *are not validated*, they are simply
passed through to the instance. The hints are primarily for your use as the developer. You can specify defaults for any
field, otherwise they will default to `None`.

When creating `Records` with annotations from geojson, the fields in the geojson's `properties` must match
the names in the annotations. Only the fields which are annotated on the class will be used, so this is a useful way
to filter fields which are not needed. If you are instantiating a `Record` directly, then the geometry must be the
first argument, and all attributes must be passed in as kwargs so they are named explicitly.

Modelling our data using classes has the advantage of allowing us to easily add custom behavior or derived attributes
to our data:

.. code-block:: python

    import meridian

    class PowerPlant(meridian.Record):
        install_mw: float
        total_mw: float

		@property
		def capacity_factor(self) -> float:
			"""https://en.wikipedia.org/wiki/Capacity_factor"""
			return self.total_mw / self.install_mw * 100





.. _design

Design Goals
=============

Some items which are important to me, in no particular order:
 - Pythonicity. should be interoperable with standard library tools and be intuitive to use.
 - Efficiency. Memory use is kept as low as possible and operations are optimized when appropriate.
 - Type hinting wherever possible.
 - Strong support for dataset attribution.


Meridian's `Record` models draw strong inspiration from `pydantic`'s `BaseModel`, choosing to re-invent a small
part of that wheel for the purpose of efficiency and narrowing of focus.


.. _benchmarks

Benchmarks
===========

A dataset opened with Meridian can use up to half as much memory as the same dataset in GeoPandas,
depending on the characteristics of the geometry.