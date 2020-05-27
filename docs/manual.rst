.. _manual:

=======================
Meridian User Manual
=======================


.. _intro:

Introduction
============

Geospatial data and processes which deal with it have a rather significant bit of jargon associated with them, and that
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
so you can use familiar terminologies, tools, and mental models when you're dealing with it.

Meridian is not trying to displace a tool like Geopandas, which is excellent for exploring and understanding datasets.
Instead, Meridian wants to be an efficient option for intensive and repeated geospatial processing applications
once data exploration is concluded.

.. _core:

Core Models
============


