# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Download(Component):
    """A Download component.
The Download component opens a download dialog when the data property (dict of filename, content, and type) changes.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- base64 (boolean; default False):
    Default value for base64.

- data (dict; optional):
    When set, a download is invoked using a Blob.

    `data` is a dict with keys:

    - base64 (boolean; optional)

    - content (boolean | number | string | dict | list; required)

    - filename (string; required)

    - mime_type (string; optional)

- mime_type (string; default "text/plain"):
    Default value for mime_type."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, data=Component.UNDEFINED, base64=Component.UNDEFINED, mime_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'base64', 'data', 'mime_type']
        self._type = 'Download'
        self._namespace = 'dash_extensions'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'base64', 'data', 'mime_type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Download, self).__init__(**args)
