# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Burger(Component):
    """A Burger component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    The class of the component.

- customBurgerIcon (boolean; optional)

- customCrossIcon (boolean; optional)

- disableAutoFocus (boolean; optional)

- disableCloseOnEsc (boolean; optional)

- disableOverlayClick (boolean; optional)

- effect (a value equal to: "slide", "stack", "elastic", "bubble", "push", "pushRotate", "scaleDown", "scaleRotate", "fallDown", "reveal"; default "slide")

- height (string; default "100%")

- isOpen (boolean; optional)

- noOverlay (boolean; optional)

- noTransition (boolean; optional)

- outerContainerId (string; optional)

- pageWrapId (string; optional)

- right (boolean; optional)

- style (dict; optional)

- width (string; default "300px")"""
    @_explicitize_args
    def __init__(self, children=None, width=Component.UNDEFINED, height=Component.UNDEFINED, effect=Component.UNDEFINED, pageWrapId=Component.UNDEFINED, outerContainerId=Component.UNDEFINED, right=Component.UNDEFINED, disableCloseOnEsc=Component.UNDEFINED, noOverlay=Component.UNDEFINED, disableOverlayClick=Component.UNDEFINED, noTransition=Component.UNDEFINED, customBurgerIcon=Component.UNDEFINED, customCrossIcon=Component.UNDEFINED, disableAutoFocus=Component.UNDEFINED, style=Component.UNDEFINED, isOpen=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'customBurgerIcon', 'customCrossIcon', 'disableAutoFocus', 'disableCloseOnEsc', 'disableOverlayClick', 'effect', 'height', 'isOpen', 'noOverlay', 'noTransition', 'outerContainerId', 'pageWrapId', 'right', 'style', 'width']
        self._type = 'Burger'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'customBurgerIcon', 'customCrossIcon', 'disableAutoFocus', 'disableCloseOnEsc', 'disableOverlayClick', 'effect', 'height', 'isOpen', 'noOverlay', 'noTransition', 'outerContainerId', 'pageWrapId', 'right', 'style', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Burger, self).__init__(children=children, **args)
