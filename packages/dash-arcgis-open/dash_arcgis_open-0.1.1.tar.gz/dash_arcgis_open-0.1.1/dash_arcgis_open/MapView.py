# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MapView(Component):
    """A MapView component.


Keyword arguments:

- children (boolean | number | string | dict | list; optional)

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- basemap (string; default 'streets-navigation-vector')

- breakpoints (dict; default {        xsmall: 544,        small: 768,        medium: 992,        large: 1200,        xlarge: 1600,    })

    `breakpoints` is a dict with keys:

    - large (number; required)

    - medium (number; required)

    - small (number; required)

    - xlarge (number; required)

    - xsmall (number; required)

- center (list of numbers; default [0.13, 51.51])

- constraints (boolean | number | string | dict | list; optional)

- extent (dict; optional)

    `extent` is a dict with keys:

    - xmax (number; required)

    - xmin (number; required)

    - ymax (number; required)

    - ymin (number; required)

- heightBreakpoint (string; optional)

- style (boolean | number | string | dict | list; optional)

- widthBreakpoint (string; optional)

- zoom (number; default 10)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_arcgis_open'
    _type = 'MapView'
    @_explicitize_args
    def __init__(self, children=None, basemap=Component.UNDEFINED, center=Component.UNDEFINED, zoom=Component.UNDEFINED, id=Component.UNDEFINED, style=Component.UNDEFINED, extent=Component.UNDEFINED, breakpoints=Component.UNDEFINED, widthBreakpoint=Component.UNDEFINED, heightBreakpoint=Component.UNDEFINED, constraints=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'basemap', 'breakpoints', 'center', 'constraints', 'extent', 'heightBreakpoint', 'style', 'widthBreakpoint', 'zoom']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'basemap', 'breakpoints', 'center', 'constraints', 'extent', 'heightBreakpoint', 'style', 'widthBreakpoint', 'zoom']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(MapView, self).__init__(children=children, **args)
