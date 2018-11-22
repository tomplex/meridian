import typing
import sys as _sys
import warnings

from keyword import iskeyword as _iskeyword
from shapely import geometry


_spatialdata_class_template = """\
from builtins import property as _property, tuple as _tuple
from operator import itemgetter as _itemgetter
from collections import OrderedDict

class {typename}(tuple):
    '{typename}({arg_list})'

    __slots__ = ()

    _fields = {field_names!r}

    def __new__(_cls, {arg_list}):
        'Create new instance of {typename}({arg_list})'
        return _tuple.__new__(_cls, ({arg_list}))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return self.__class__.__name__ + '({repr_fmt})' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return OrderedDict(zip(self._fields, self))

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    @property
    def __geo_interface__(self):
        'Create a GeoJSON feature for this spatialdata.'
        d = self._asdict()
        del d['bounds']
        return {{
            'type': 'Feature',
            'id': d.pop('id'),
            'geometry': d.pop('geom').__geo_interface__,
            'properties': {{**d}}
        }}
    
    @property
    def _geom(self):
        'Adding _geom as a property allows a spatialdata to interact seamlessly with shapely geometries. All methods on geometries'
        'use the _geom property to access the underlying C objects pointer, so exposing it this way makes shapely think'
        'its simply acting on another geometry object.'
        return self.geom._geom
    
    @property
    def type(self):
        return self.geom.type
    
    @property
    def area(self):
        "Easy access to the spatialdata geometry's area."
        return self.geom.area
    
    def intersects(self, other):
        return self.geom.intersects(other)
        
    def within(self, other):
        return self.geom.within(other)
    
    def contains(self, other):
        return self.geom.contains(other)
    
    
    

{field_defs}
"""

_repr_template = '{name}=%r'

_field_template = '''\
    {name} = _property(_itemgetter({index:d}), doc='Alias for field number {index:d}')
'''


def _spatialdata_factory(typename, field_names, *, verbose=False, rename=False, module=None):
    """Returns a new subclass of tuple with named fields.

    Pretty much an exact copy of namedtuple from collections, but I want more control over what the spatialdata
    namedtuple looks like and how it behaves.

    By implementing this ourselves, we can change the class template above and add, for instance, the __geo_interface__
    property.

    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = list(map(str, field_names))
    typename = str(typename)
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not name.isidentifier()
                or _iskeyword(name)
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)
    for name in [typename] + field_names:
        if type(name) is not str:
            raise TypeError('Type names and field names must be strings')
        if not name.isidentifier():
            raise ValueError('Type names and field names must be valid '
                             'identifiers: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    # Fill-in the class template
    class_definition = _spatialdata_class_template.format(
        typename = typename,
        field_names = tuple(field_names),
        num_fields = len(field_names),
        arg_list = repr(tuple(field_names)).replace("'", "")[1:-1],
        repr_fmt = ', '.join(_repr_template.format(name=name)
                             for name in field_names),
        field_defs = '\n'.join(_field_template.format(index=index, name=name)
                               for index, name in enumerate(field_names))
    )

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(__name__='namedtuple_%s' % typename)
    exec(class_definition, namespace)
    result = namespace[typename]
    result._source = class_definition
    if verbose:
        print(result._source)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython), or where the user has
    # specified a particular module.
    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    if module is not None:
        result.__module__ = module

    return result


def _get_spatialdata_factory(geojson: dict) -> typing.Callable:
    """
    Create a factory function which will create spatialdata named tuples for the user's input data.

    We take a single geojson of the user's data to determine what the namedtuple that will hold it
    should look like. We'll use the names of the keys in the `properties` dict to add the correct field names
    to our spatialdata object. We also add the id, geom, and bounds properties to each one - these are required
    for the library to work properly. If the user's input data has an id field in the top level, then we'll pass
    that through to the spatialdata object. Otherwise we'll use the one generated when `enumerating` the input data.


    Args:
        geojson: A sample of the inpit geojson.

    Returns:
        factory: a factory function which will create spatialdata from geojson objects.
    """

    fields = list(geojson.get('properties', {}).keys())

    spatial_data = _spatialdata_factory('spatialdata', field_names=set(fields + ['id', 'geom', 'bounds']))

    def with_id_factory(geojson: dict, idx: int):
        props = geojson.get('properties', {})
        geom = geometry.shape(geojson.get('geometry'))

        return spatial_data(id=geojson.get('id'), geom=geom, bounds=geom.bounds, **props)

    def without_id_factory(geojson: dict, idx: int):
        props = geojson.get('properties', {})
        geom = geometry.shape(geojson.get('geometry'))

        return spatial_data(id=idx, geom=geom, bounds=geom.bounds, **props)

    if 'id' in geojson:
        return with_id_factory

    return without_id_factory


def spatialdata_to_geojson(spatialdata):
    """
    Helper function to convert a spatial data object back into GeoJSON. Mostly provided in the situation where a user
    wishes to build up a new SpatialDataset with a subset of data from an existing one, or with processing added.

    Args:
        spatialdata: a `meridian` spatialdata namedtuple

    Returns:
        dict - GeoJSON representation of the spatialdata object

    """
    warnings.warn("Deprecation warning: this function will be deprecated soon. Use spatialdata.__geo_interface__ instead.")
    return spatialdata.__geo_interface__