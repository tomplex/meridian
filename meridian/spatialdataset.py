import rtree
import typing

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


def _check_bounds(query):
    if not hasattr(query, 'bounds'):
        raise AttributeError("Query argument to SpatialData methods must implement bounds property returning (xmin, ymin, xmax, ymax)")


class SpatialData(typing.NamedTuple):
    id: int = None
    geom: BaseGeometry = None
    properties: dict = None

    @property
    def _geom(self):
        """
        Adding _geom as a property allows a spatialdata to interact seamlessly with shapely geometries. All methods on geometries
        use the _geom property to access the underlying C objects pointer, so exposing it this way makes shapely think
        its simply acting on another geometry object.
        """
        return self.geom._geom

    @property
    def __geo_interface__(self):
        return {
            'type': 'Feature',
            'id': self.id,
            'geometry': self.geom.__geo_interface__,
            'properties': self.properties
        }

    def __getattr__(self, item):
        return self.properties[item]

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

    def __init__(self, data: typing.Iterable):
        self.__data = dict()
        self.__rtree: rtree.Rtree = None

        self.__load(data)

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data.values())

    def __load(self, data_stream):
        for idx, geojson in enumerate(data_stream):

            record = SpatialData(
                id=geojson.get('id') or idx,
                geom=shape(geojson.get('geometry')),
                properties=geojson.get('properties', {})

            )
            self.__data[idx] = record

        properties = rtree.index.Property()
        properties.dimension = 2
        properties.leaf_capacity = 1000
        properties.fill_factor = 0.9

        self.__rtree = rtree.Rtree(((idx, sd.bounds, None) for idx, sd in self.__data.items()), properties=properties)

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
            generator of intersecting objects
        """
        _check_bounds(query)
        return list(self.__data[i] for i in self.__rtree.intersection(query.bounds))

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
            Generator of nearest spatialdata records
        """
        _check_bounds(query)
        return list(self.__data[i] for i in self.__rtree.nearest(query.bounds, num_results))
