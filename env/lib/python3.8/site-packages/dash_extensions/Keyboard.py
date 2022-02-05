# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Keyboard(Component):
    """A Keyboard component.
The Keyboard component listens for keyboard events.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- captureKeys (list of strings; optional):
    The keys to capture. Defaults to all keys.

- eventProps (list of strings; default ["key", "altKey", "ctrlKey", "shiftKey","metaKey", "repeat"]):
    The event properties to forward to dash, see
    https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent.

- keydown (dict; optional):
    keydown (dict) the object that holds the result of the key down
    event. It is a dictionary with the following keys:      \"key\",
    \"altKey\", \"ctrlKey\", \"shiftKey\",\"metaKey\", \"repeat\".
    Those keys have the following values:     - key (str) which key is
    pressed    - altKey (bool) whether the Alt key is pressed    -
    ctrlKey (bool) Ctrl key is pressed    - shiftKey (bool) Shift key
    is pressed    - metaKey (bool) Meta key is pressed (Mac: Command
    key or PC: Windows key)    - repeat (bool) whether the key is held
    down.

- keys_pressed (dict; optional):
    keys_pressed (dict) is a dict of objects like keydown for all keys
    currently pressed.

- keyup (dict; optional):
    keyup (dict) the object that holds the result of the key up event.
    Structure like keydown.

- n_keydowns (number; default 0):
    A counter, which is incremented on each key down event, similar to
    n_clicks for buttons.

- n_keyups (number; default 0):
    A counter, which is incremented on each key up event, similar to
    n_clicks for buttons."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, eventProps=Component.UNDEFINED, captureKeys=Component.UNDEFINED, keydown=Component.UNDEFINED, keyup=Component.UNDEFINED, keys_pressed=Component.UNDEFINED, n_keydowns=Component.UNDEFINED, n_keyups=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'captureKeys', 'eventProps', 'keydown', 'keys_pressed', 'keyup', 'n_keydowns', 'n_keyups']
        self._type = 'Keyboard'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'captureKeys', 'eventProps', 'keydown', 'keys_pressed', 'keyup', 'n_keydowns', 'n_keyups']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Keyboard, self).__init__(**args)
