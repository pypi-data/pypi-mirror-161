# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Rnd(Component):
    """A Rnd component.
A resizable and draggable component

Keyword arguments:

- children (dash component | list | string; optional):
    The ID used to identify this component in Dash callbacks.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- bounds (string; optional):
    `bounds?: string;`  Specifies movement boundaries. Accepted
    values: - `parent` restricts movement within the node's
    offsetParent (nearest node with position relative or absolute) -
    `window`, `body`, or - Selector, like `.fooClassName`.

- cancel (string; optional):
    `cancel?: string;`  The cancel property disables specifies a
    selector to be used to prevent drag initialization (e.g. .body).

- className (string; optional):
    `className?: string;`  The className property is used to set the
    custom className of the component.

- default (dict; required):
    `default: { x: number; y: number; width?: number | string;
    height?: number | string; };`  The width and height property is
    used to set the default size of the component. For example, you
    can set 300, '300px', 50%. If omitted, set 'auto'. The x and y
    property is used to set the default position of the component.

    `default` is a dict with keys:

    - height (number

      Or string; optional)

    - width (number | string; optional)

    - x (number; optional)

    - y (number; optional) | dict with keys:

    - x (number; optional)

    - y (number; optional)

- disableDragging (boolean; optional):
    `disableDragging?: boolean;`  The disableDragging property
    disables dragging completely.

- dragAxis (a value equal to: 'x', 'y', 'both', 'none'; optional):
    `dragAxis?: 'x' | 'y' | 'both' | 'none'`  The direction of allowed
    movement (dragging) allowed ('x','y','both','none').

- dragGrid (list of numbers; optional):
    `dragGrid?: [number, number];`  The dragGrid property is used to
    specify the increments that moving should snap to. Defaults to [1,
    1].

- dragHandleClassName (string; optional):
    `dragHandleClassName?: string;`  Specifies a selector to be used
    as the handle that initiates drag. Example: handle.

- enableResizing (dict; optional):
    `enableResizing?: ?Enable;`  The enableResizing property is used
    to set the resizable permission of the component. The permission
    of top, right, bottom, left, topRight, bottomRight, bottomLeft,
    topLeft direction resizing. If omitted, all resizer are enabled.
    If you want to permit only right direction resizing, set {
    top:False, right:True, bottom:False, left:False, topRight:False,
    bottomRight:False, bottomLeft:False, topLeft:False }.  ``` export
    type Enable = {   bottom?: boolean;   bottomLeft?: boolean;
    bottomRight?: boolean;   left?: boolean;   right?: boolean;
    top?: boolean;   topLeft?: boolean;   topRight?: boolean; } |
    boolean ```.

    `enableResizing` is a dict with keys:

    - bottom (boolean; optional)

    - bottomLeft (boolean; optional)

    - bottomRight (boolean; optional)

    - left (boolean; optional)

    - right (boolean; optional)

    - top (boolean; optional)

    - topLeft (boolean; optional)

    - topRight (boolean; optional) | boolean

- enableUserSelectHack (boolean; optional)

- lockAspectRatio (boolean | number; optional):
    `lockAspectRatio?: boolean | number;`  The lockAspectRatio
    property is used to lock aspect ratio. Set to True to lock the
    aspect ratio based on the initial size. Set to a numeric value to
    lock a specific aspect ratio (such as 16/9). If set to numeric,
    make sure to set initial height/width to values with correct
    aspect ratio. If omitted, set False.

- lockAspectRatioExtraHeight (number; optional):
    `lockAspectRatioExtraHeight?: number;`  The
    lockAspectRatioExtraHeight property enables a resizable component
    to maintain an aspect ratio plus extra height. For instance, a
    video could be displayed 16:9 with a 50px header bar. If omitted,
    set 0.

- lockAspectRatioExtraWidth (number; optional):
    `lockAspectRatioExtraWidth?: number;`  The
    lockAspectRatioExtraWidth property enables a resizable component
    to maintain an aspect ratio plus extra width. For instance, a
    video could be displayed 16:9 with a 50px side bar. If omitted,
    set 0.

- maxHeight (number | string; optional):
    `maxHeight?: number | string;`  The maxHeight property is used to
    set the maximum height of the component. For example, you can set
    300, '300px', 50%.

- maxWidth (number | string; optional):
    `maxWidth?: number | string;`  The maxWidth property is used to
    set the maximum width of the component. For example, you can set
    300, '300px', 50%.

- minHeight (number | string; optional):
    `minHeight?: number | string;`  The minHeight property is used to
    set the minimum height of the component. For example, you can set
    300, '300px', 50%.

- minWidth (number | string; optional):
    `minWidth?: number | string;`  The minWidth property is used to
    set the minimum width of the component. For example, you can set
    300, '300px', 50%.

- position (dict; optional):
    `position?: { x: number, y: number };`  The position property is
    used to set position of the component. Use position if you need to
    control size state by yourself.

    `position` is a dict with keys:

    - x (number; optional)

    - y (number; optional)

- resizeGrid (list of numbers; optional):
    `resizeGrid?: [number, number];`  The resizeGrid property is used
    to specify the increments that resizing should snap to. Defaults
    to [1, 1].

- resizeHandleClasses (dict; optional):
    `resizeHandleClasses?: HandleClasses;`  The resizeHandleClasses
    property is used to set the className of one or more resize
    handles.  ``` type HandleClasses = {   bottom?: string;
    bottomLeft?: string;   bottomRight?: string;   left?: string;
    right?: string;   top?: string;   topLeft?: string;   topRight?:
    string; } ```.

    `resizeHandleClasses` is a dict with keys:

    - bottom (string; optional)

    - bottomLeft (string; optional)

    - bottomRight (string; optional)

    - left (string; optional)

    - right (string; optional)

    - top (string; optional)

    - topLeft (string; optional)

    - topRight (string; optional)

- resizeHandleComponent (dict; optional):
    `resizeHandleComponent?: HandleCompoent;`  The
    resizeHandleComponent allows you to pass a custom React component
    as the resize handle.  ``` type HandleComponent = {   top?:
    React.ReactElement<any>;   right?: React.ReactElement<any>;
    bottom?: React.ReactElement<any>;   left?:
    React.ReactElement<any>;   topRight?: React.ReactElement<any>;
    bottomRight?: React.ReactElement<any>;   bottomLeft?:
    React.ReactElement<any>;   topLeft?: React.ReactElement<any>; }
    ```.

    `resizeHandleComponent` is a dict with keys:

    - bottom (dash component; optional)

    - bottomLeft (dash component; optional)

    - bottomRight (dash component; optional)

    - left (dash component; optional)

    - right (dash component; optional)

    - top (dash component; optional)

    - topLeft (dash component; optional)

    - topRight (dash component; optional)

- resizeHandleStyles (dict; optional):
    `resizeHandleStyles?: HandleStyles;`  The resizeHandleStyles
    property is used to override the style of one or more resize
    handles. Only the axis you specify will have its handle style
    replaced. If you specify a value for right it will completely
    replace the styles for the right resize handle, but other handle
    will still use the default styles.  ``` export type HandleStyles =
    {   bottom?: React.CSSProperties,   bottomLeft?:
    React.CSSProperties,   bottomRight?: React.CSSProperties,   left?:
    React.CSSProperties,   right?: React.CSSProperties,   top?:
    React.CSSProperties,   topLeft?: React.CSSProperties,   topRight?:
    React.CSSProperties } ```.

    `resizeHandleStyles` is a dict with keys:

    - bottom (dict; optional)

    - bottomLeft (dict; optional)

    - bottomRight (dict; optional)

    - left (dict; optional)

    - right (dict; optional)

    - top (dict; optional)

    - topLeft (dict; optional)

    - topRight (dict; optional)

- resizeHandleWrapperClass (string; optional):
    `resizeHandleWrapperClass?: string;`  The resizeHandleWrapperClass
    property is used to set css class name of resize handle
    wrapper(span) element.

- resizeHandleWrapperStyle (dict; optional):
    `resizeHandleWrapperStyle?: Style;`  The resizeHandleWrapperStyle
    property is used to set css class name of resize handle
    wrapper(span) element.

- scale (number; optional):
    `scale?: number;` Specifies the scale of the canvas you are
    dragging or resizing this element on. This allows you to, for
    example, get the correct drag / resize deltas while you are zoomed
    in or out via a transform or matrix in the parent of this element.
    If omitted, set 1.

- size (dict; optional):
    `size?: { width: (number | string), height: (number | string) };`
    The size property is used to set size of the component. For
    example, you can set 300, '300px', 50%. Use size if you need to
    control size state by yourself.

    `size` is a dict with keys:

    - height (number | string; optional)

    - width (number | string; optional)

- style (dict; optional):
    `style?: { [key: string]: string };`  The style property is used
    to set the custom style of the component."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, default=Component.REQUIRED, size=Component.UNDEFINED, position=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, minWidth=Component.UNDEFINED, minHeight=Component.UNDEFINED, maxWidth=Component.UNDEFINED, maxHeight=Component.UNDEFINED, resizeGrid=Component.UNDEFINED, dragGrid=Component.UNDEFINED, lockAspectRatio=Component.UNDEFINED, lockAspectRatioExtraWidth=Component.UNDEFINED, scale=Component.UNDEFINED, lockAspectRatioExtraHeight=Component.UNDEFINED, dragHandleClassName=Component.UNDEFINED, resizeHandleStyles=Component.UNDEFINED, resizeHandleClasses=Component.UNDEFINED, resizeHandleComponent=Component.UNDEFINED, resizeHandleWrapperClass=Component.UNDEFINED, resizeHandleWrapperStyle=Component.UNDEFINED, enableResizing=Component.UNDEFINED, disableDragging=Component.UNDEFINED, cancel=Component.UNDEFINED, dragAxis=Component.UNDEFINED, bounds=Component.UNDEFINED, enableUserSelectHack=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'bounds', 'cancel', 'className', 'default', 'disableDragging', 'dragAxis', 'dragGrid', 'dragHandleClassName', 'enableResizing', 'enableUserSelectHack', 'lockAspectRatio', 'lockAspectRatioExtraHeight', 'lockAspectRatioExtraWidth', 'maxHeight', 'maxWidth', 'minHeight', 'minWidth', 'position', 'resizeGrid', 'resizeHandleClasses', 'resizeHandleComponent', 'resizeHandleStyles', 'resizeHandleWrapperClass', 'resizeHandleWrapperStyle', 'scale', 'size', 'style']
        self._type = 'Rnd'
        self._namespace = 'factory_component'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'bounds', 'cancel', 'className', 'default', 'disableDragging', 'dragAxis', 'dragGrid', 'dragHandleClassName', 'enableResizing', 'enableUserSelectHack', 'lockAspectRatio', 'lockAspectRatioExtraHeight', 'lockAspectRatioExtraWidth', 'maxHeight', 'maxWidth', 'minHeight', 'minWidth', 'position', 'resizeGrid', 'resizeHandleClasses', 'resizeHandleComponent', 'resizeHandleStyles', 'resizeHandleWrapperClass', 'resizeHandleWrapperStyle', 'scale', 'size', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['default']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Rnd, self).__init__(children=children, **args)
