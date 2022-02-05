# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class BeforeAfter(Component):
    """A BeforeAfter component.
A light wrapper of BeforeAfterSlider.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- after (string; optional)

- afterClassName (string; optional)

- afterProps (dict; optional)

- before (string; optional)

- beforeClassName (string; optional)

- beforeProps (dict; optional)

- className (string; optional):
    The class of the component.

- defaultProgress (number; optional)

- height (number; optional)

- width (number; optional)"""
    @_explicitize_args
    def __init__(self, children=None, before=Component.UNDEFINED, after=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, defaultProgress=Component.UNDEFINED, beforeClassName=Component.UNDEFINED, afterClassName=Component.UNDEFINED, beforeProps=Component.UNDEFINED, afterProps=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'after', 'afterClassName', 'afterProps', 'before', 'beforeClassName', 'beforeProps', 'className', 'defaultProgress', 'height', 'width']
        self._type = 'BeforeAfter'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'after', 'afterClassName', 'afterProps', 'before', 'beforeClassName', 'beforeProps', 'className', 'defaultProgress', 'height', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(BeforeAfter, self).__init__(children=children, **args)
