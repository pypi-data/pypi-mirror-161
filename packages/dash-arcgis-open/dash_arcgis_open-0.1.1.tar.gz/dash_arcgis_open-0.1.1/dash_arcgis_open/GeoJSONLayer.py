# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class GeoJSONLayer(Component):
    """A GeoJSONLayer component.


Keyword arguments:

- id (string; required):
    ID of the component.

- url (string; required):
    URL of the GeoJSON file."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_arcgis_open'
    _type = 'GeoJSONLayer'
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, url=Component.REQUIRED, **kwargs):
        self._prop_names = ['id', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id', 'url']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(GeoJSONLayer, self).__init__(**args)
