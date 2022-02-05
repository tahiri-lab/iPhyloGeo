# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Monitor(Component):
    """A Monitor component.
The Sync component makes it possible to synchronize states between components.

Keyword arguments:

- children (list of a list of or a singular dash component, string or numbers; optional):
    The children of this component. Must be a list of components with
    length > 1.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    A custom class name.

- data (dict; optional)

- probes (dict; optional):
    List of probes. Each link is a list of dicts that specify which
    properties each probe records.

    `probes` is a dict with strings as keys and values of type list of
    list of strings | dict with keys:

    - id (string | dict; optional)

    - prop (boolean | number | string | dict | list; required)s

- style (dict; optional):
    The CSS style of the component."""
    @_explicitize_args
    def __init__(self, children=None, probes=Component.UNDEFINED, data=Component.UNDEFINED, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'data', 'probes', 'style']
        self._type = 'Monitor'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'data', 'probes', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Monitor, self).__init__(children=children, **args)
