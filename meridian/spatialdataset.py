import itertools

import rtree
import typing

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


def _check_bounds(query):
    if not hasattr(query, 'bounds'):
        raise AttributeError("Query argument to SpatialData methods must implement bounds property returning (xmin, ymin, xmax, ymax)")


class SpatialData(typing.NamedTuple):
    geom: BaseGeometry = None
    properties: typing.NamedTuple = None

    @property
    def _geom(self):
        """
        Adding _geom as a property allows a spatialdata to interact seamlessly with shapely geometries. All methods on
        geometries use the _geom property to access the underlying C objects pointer, so exposing it this way makes
        shapely think it's simply acting on another geometry object.
        """
        return self.geom._geom

    @property
    def __geo_interface__(self):
        return {
            'type': 'Feature',
            'geometry': self.geom.__geo_interface__,
            'properties': self.properties._asdict()
        }

    def __getattr__(self, item):
        return getattr(self.properties, item)

    @property
    def type(self):
        return self.geom.type

    @property
    def bounds(self):
        return self.geom.bounds

    @property
    def area(self):
        """
        Easy access to the spatialdata geometry's area.

        """
        return self.geom.area

    def intersects(self, other):
        return self.geom.intersects(other)

    def within(self, other):
        return self.geom.within(other)

    def contains(self, other):
        return self.geom.contains(other)


class SpatialDataset:
    """
    The SpatialDataset is the core piece of meridian. It wraps spatial data and exposes methods to manage it.

    """

    def __init__(self, data: typing.Union[typing.Sequence, typing.Iterable], properties: rtree.index.Property = None):
        if hasattr(data, '__next__'):
            # It's a generator / iterator
            first = next(data)
            # reconstruct our initial iterator by chaining the first item with the
            # rest of the iterator
            data = itertools.chain(iter([first]), data)
        else:
            # it's a sequence
            first = data[0]

        if isinstance(first, SpatialData):
            self.__data = tuple(data)
        else:
            fields = [(name, type(value)) for name, value in first['properties'].items()]
            record_properties = typing.NamedTuple('properties', fields)

            def make_properties(geojson):
                props = geojson.get('properties', {})
                if props:
                    return record_properties(**props)
                return None

            self.__data = tuple(SpatialData(
                geom=shape(geojson.get('geometry')),
                properties=make_properties(geojson)
            ) for geojson in data)

        if properties is None:
            properties = rtree.index.Property()
            properties.dimension = 2
            properties.fill_factor = 0.999
            properties.leaf_capacity = 1000

        gen = ((idx, sd.bounds, None) for idx, sd in enumerate(self.__data))
        self.__rtree = rtree.Rtree(gen, properties=properties)

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __getitem__(self, item):
        return self.__data[item]

    @property
    def bounds(self):
        """
        The bounds of the SpatialDataset.

        Returns: 4-tuple (xmin, ymin, xmax, ymax)
        """
        return self.__rtree.bounds

    def intersects(self, query) -> bool:
        """
        Check if the SpatialDataset intersects with the query object.
        Args:
            query:

        Returns:
            bool

        """
        _check_bounds(query)
        return self.__rtree.count(query.bounds) != 0

    def intersection(self, query):
        """
        Find the intersection of the input geometry / spatial data and the SpatialDataset.

        Args:
            query: an object which exposes a `bounds` property of the (xmin, ymin, xmax, ymax) format.

        Returns:
            SpatialDataset of intersecting objects
        """
        _check_bounds(query)
        return SpatialDataset(self.__data[i] for i in self.__rtree.intersection(query.bounds))

    def count(self, query) -> int:
        """
        Count the number of objects in the SpatialDataset which intersect with the query object.

        Args:
            query: an object which exposes a `bounds` property of the (xmin, ymin, xmax, ymax) format.

        Returns:
            int
        """
        _check_bounds(query)
        return self.__rtree.count(query.bounds)

    def nearest(self, query, num_results=1):
        """
        Find the nearest n objects in the SpatialDataset to the query object.

        Args:
            query:
            num_results:

        Returns:
            SpatialDataset of nearest spatialdata records
        """
        _check_bounds(query)
        return SpatialDataset(self.__data[i] for i in self.__rtree.nearest(query.bounds, num_results))
