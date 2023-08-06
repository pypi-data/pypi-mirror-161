# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class TextEditor(Component):
    """A TextEditor component.


Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    className  Class name for the editor container.

- defaultLanguage (string; default 'python'):
    defaultLanguage  language of the current model.

- defaultPath (string; optional):
    defaultPath  Default path of the current model. Will be passed as
    the third argument to .createModel method -
    monaco.editor.createModel(..., ...,
    monaco.Uri.parse(defaultPath)).

- defaultValue (string; optional):
    defaultValue  Default value of the current model.

- height (string | number; default '100%'):
    height  union: Height of the editor wrapper.

- keepCurrentModel (boolean; default False):
    keepCurrentModel  Indicator whether to dispose the current model
    when the Editor is unmounted or not.

- language (string; optional):
    language  Language of the current model (all languages that are
    supported by monaco-editor).

- line (number; optional):
    line  The line to jump on it.

- loading (dash component | string; default 'Loading...'):
    loading  The loading screen before the editor will be mounted.

- options (dict; optional):
    options  IStandaloneEditorConstructionOptions.

- overrideServices (dict; optional):
    overrideServices  IEditorOverrideServices.

- path (string; optional):
    path  Path of the current model. Will be passed as the third
    argument to .createModel method - monaco.editor.createModel(...,
    ..., monaco.Uri.parse(defaultPath)).

- saveViewState (boolean; default True):
    saveViewState  Indicator whether to save the models' view states
    between model changes or not.

- theme (a value equal to: "light", "vs-dark"; default 'light'):
    theme  The theme for the monaco. Available options \"vs-dark\" |
    \"light\". Define new themes by monaco.editor.defineTheme.

- value (string; optional):
    value  Value of the current model.

- width (string | number; default '100%'):
    width  union: Width of the editor wrapper.

- wrapperProps (dict; optional):
    wrapperProps  Props applied to the wrapper element."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, defaultValue=Component.UNDEFINED, defaultLanguage=Component.UNDEFINED, defaultPath=Component.UNDEFINED, value=Component.UNDEFINED, language=Component.UNDEFINED, path=Component.UNDEFINED, theme=Component.UNDEFINED, line=Component.UNDEFINED, loading=Component.UNDEFINED, options=Component.UNDEFINED, overrideServices=Component.UNDEFINED, saveViewState=Component.UNDEFINED, keepCurrentModel=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, className=Component.UNDEFINED, wrapperProps=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'defaultLanguage', 'defaultPath', 'defaultValue', 'height', 'keepCurrentModel', 'language', 'line', 'loading', 'options', 'overrideServices', 'path', 'saveViewState', 'theme', 'value', 'width', 'wrapperProps']
        self._type = 'TextEditor'
        self._namespace = 'factory_component'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'defaultLanguage', 'defaultPath', 'defaultValue', 'height', 'keepCurrentModel', 'language', 'line', 'loading', 'options', 'overrideServices', 'path', 'saveViewState', 'theme', 'value', 'width', 'wrapperProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(TextEditor, self).__init__(**args)
