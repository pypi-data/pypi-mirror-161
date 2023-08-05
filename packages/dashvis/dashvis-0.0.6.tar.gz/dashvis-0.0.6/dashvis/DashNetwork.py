# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashNetwork(Component):
    """A DashNetwork component.
A full implementation of [vis.js](https://visjs.github.io/vis-network/docs/network/)
Network component for Dash Plotly.
Useful for displaying dynamic, automatically organised, customizable network views.

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- DOMtoCanvas (dict; optional):
    Function call. Pass your values into this property and read off
    the results from the same property. This function converts DOM
    coordinates to coordinate on the canvas. Input and output are in
    the form of {x:Number,y:Number}. The DOM values are relative to
    the network container.

    `DOMtoCanvas` is a dict with keys:

    - x (number; optional)

    - y (number; optional)

- addEdgeMode (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Go into addEdge
    mode. The explanation from addNodeMode applies here as well.
    Returns: None.

- addNodeMode (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Go into addNode
    mode. Having edit mode or manipulation enabled is not required. To
    get out of this mode, call disableEditMode(). The callback
    functions defined in handlerFunctions still apply. To use these
    methods without having the manipulation GUI, make sure you set
    enabled to False. Returns: None.

- afterDrawing (dict; optional):
    Read-only prop. To use this, make sure that `enableOtherEvents` is
    set to `True`, or that `enableOtherEvents` is a list that contains
    this event type. Fired after drawing on the canvas has been
    completed. Can be used to draw on top of the network.

- animationFinished (dict; optional):
    Read-only prop. To use this, make sure that `enableOtherEvents` is
    set to `True`, or that `enableOtherEvents` is a list that contains
    this event type. Fired when an animation is finished.

- beforeDrawing (dict; optional):
    Read-only prop. To use this, make sure that `enableOtherEvents` is
    set to `True`, or that `enableOtherEvents` is a list that contains
    this event type.    Fired after the canvas has been cleared,
    scaled and translated to the viewing position but before all edges
    and nodes are drawn. Can be used to draw behind the network.

- blurEdge (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired if the option interaction:{hover:True} is
    enabled and the mouse moved away from an edge it was hovering over
    before.

- blurNode (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired if the option interaction:{hover:True} is
    enabled and the mouse moved away from a node it was hovering over
    before.

- canvasToDOM (dict; optional):
    Function call. Pass your values into this property and read off
    the results from the same property. This function converts canvas
    coordinates to coordinate on the DOM. Input and output are in the
    form of {x:Number,y:Number}. The DOM values are relative to the
    network container.

    `canvasToDOM` is a dict with keys:

    - x (number; optional)

    - y (number; optional)

- click (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the user clicks the mouse of taps on a
    touchscreen device. {   nodes: [Array of selected nodeIds],
    edges: [Array of selected edgeIds],   event: [Object] original
    click event,   pointer: {     DOM: {x:pointer_x, y:pointer_y},
    canvas: {x:canvas_x, y:canvas_y}   } }  This is the structure
    common to all events. Specifically for the click event, the
    following property is added:  { ...   items: [Array of click
    items], }  Where the click items can be:   {nodeId:NodeId}
    // node with given id clicked on   {nodeId:NodeId labelId:0}  //
    label of node with given id clicked on   {edgeId:EdgeId}
    // edge with given id clicked on   {edge:EdgeId, labelId:0}   //
    label of edge with given id clicked onThe order of the items array
    is descending in z-order. Thus, to get the topmost item, get the
    value at index 0.

- cluster (dict; optional):
    Function call. Returns nothing.         Clusters the network
    according to the passed in options.         The options object is
    explained in full below. The joinCondition function is presented
    with all nodes.

    `cluster` is a dict with keys:

    - options (optional)

- clusterByConnection (dict; optional):
    Function call. Returns nothing. This method looks at the provided
    node and makes a cluster of it and all it's connected nodes. The
    behaviour can be customized by proving the options object. All
    options of this object are explained below. The joinCondition is
    only presented with the connected nodes.

    `clusterByConnection` is a dict with keys:

    - nodeId (string; optional)

    - options (optional)

- clusterByHubsize (dict; optional):
    Function call. Returns nothing. This method checks all nodes in
    the network and those with a equal or higher amount of edges than
    specified with the hubsize qualify. If a hubsize is not defined,
    the hubsize will be determined as the average value plus two
    standard deviations.  For all qualifying nodes, clusterByHubsize
    is performed on each of them. The options object is described for
    clusterByHubsize and does the same here.

    `clusterByHubsize` is a dict with keys:

    - hubsize (number; optional)

    - options (optional)

- clusterOutliers (dict; optional):
    Function call. Returns nothing.  This method will cluster all
    nodes with 1 edge with their respective connected node.  The
    options object is explained in full below.

    `clusterOutliers` is a dict with keys:

    - options (optional)

- configChange (dict; optional):
    Read-only prop. To use this, make sure that `enableOtherEvents` is
    set to `True`, or that `enableOtherEvents` is a list that contains
    this event type. Fired when a user changes any option in the
    configurator. The options object can be used with the setOptions
    method or stringified using JSON.stringify(). You do not have to
    manually put the options into the network: this is done
    automatically. You can use the event to store user options in the
    database.

- controlNodeDragEnd (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the control node drag has finished.

- controlNodeDragging (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when dragging control node. Control Edge is
    edge that is being dragged and contains ids of 'from' and 'to'
    nodes. If control node is not dragged over another node, 'to'
    field is undefined. Passes an object with properties structured
    as: {     nodes: [Array of selected nodeIds],     edges: [Array of
    selected edgeIds],     event: [Object] original click event,
    pointer: {         DOM: {x:pointer_x, y:pointer_y},
    canvas: {x:canvas_x, y:canvas_y}     },     controlEdge:
    {from:from_node_id, to:to_node_id} }.

- data (dict; default {    nodes: [{id: 1, cid: 1, label: 'Node 1', title: 'This is Node 1'},        {id: 2, cid: 1, label: 'Node 2', title: 'This is Node 2'},        {id: 3, cid: 1, label: 'Node 3', title: 'This is Node 3'},        {id: 4, label: 'Node 4', title: 'This is Node 4'},        {id: 5, label: 'Node 5', title: 'This is Node 5'}],    edges: [{from: 1, to: 3},        {from: 1, to: 2},        {from: 2, to: 4},        {from: 2, to: 5}]}):
    Graph data object describing the graph to be drawn. Pass a dict
    with two keys - 'nodes' and 'edges', set according to the vis.js
    documentation. In Dash, this property also replaces vis.js setData
    function. See
    https://visjs.github.io/vis-network/docs/network/#data.

    `data` is a dict with keys:

    - edges (list of dicts; optional)

    - nodes (list of dicts; optional)

- deleteSelected (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Delete selected.
    Having edit mode or manipulation enabled is not required. Returns:
    None.

- deselectEdge (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when an edge (or edges) has (or have) been
    deselected by the user. The previous selection is the list of
    nodes and edges that were selected before the last user event.

- deselectNode (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when a node (or nodes) has (or have) been
    deselected by the user. The previous selection is the list of
    nodes and edges that were selected before the last user event.
    Passes an object with properties structured as: {   nodes: [Array
    of selected nodeIds],   edges: [Array of selected edgeIds],
    event: [Object] original click event,   pointer: {     DOM:
    {x:pointer_x, y:pointer_y},     canvas: {x:canvas_x, y:canvas_y}
    }   },   previousSelection: {     nodes: [Array of previously
    selected nodeIds],     edges: [Array of previously selected
    edgeIds]   } }.

- destroy (boolean; default False):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Remove the network
    from the DOM and remove all Hammer bindings and references.
    Returns: None.

- disableEditMode (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Programmatically
    disable the edit mode. Similar effect to pressing the close icon
    (small cross in the corner of the toolbar). Returns: None.

- doubleClick (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the user double clicks the mouse or
    double taps on a touchscreen device. Since a double click is in
    fact 2 clicks, 2 click events are fired, followed by a double
    click event. If you do not want to use the click events if a
    double click event is fired, just check the time between click
    events before processing them.

- dragEnd (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the drag has finished.

- dragStart (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when starting a drag.

- dragging (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when dragging node(s) or the view.

- editEdgeMode (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Go into editEdge
    mode. The explanation from addNodeMode applies here as well.
    Returns: None.

- editNode (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Edit the selected
    node. The explanation from addNodeMode applies here as well.
    Returns: None.

- enableEditMode (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Programmatically
    enable the edit mode. Similar effect to pressing the edit button.
    Returns: None.

- enableHciEvents (list of strings | boolean; default False):
    Either a boolean indicating if all event callbacks, triggered by
    human interaction, selection, dragging etc., should be enabled, or
    a list of strings indicating which ones should be used. If it's a
    list, you will need to specify one of the following events:
    `click`, `doubleClick`, `oncontext`, `hold`, 'release', 'select',
    'selectNode', 'selectEdge', 'deselectNode', 'deselectEdge',
    'dragStart', 'dragging', 'dragEnd', 'controlNodeDragging',
    'controlNodeDragEnd', 'hoverNode', 'blurNode', 'hoverEdge',
    'blurEdge', 'zoom', 'showPopup', 'hidePopup'. See
    https://visjs.github.io/vis-network/docs/network/#events for more
    details.

- enableOtherEvents (list of strings | boolean; default False):
    Either a boolean indicating if all event callbacks triggered the
    canvas, rendering, view and configuration modules should be
    enabled, or a list of strings indicating which ones should be
    used. If it's a list, you will need to specify one of the
    following events: `resize`, `initRedraw`, `beforeDrawing`,
    `afterDrawing`, `animationFinished`, `configChange`. See
    https://visjs.github.io/vis-network/docs/network/#events for more
    details.

- enablePhysicsEvents (list of strings | boolean; default False):
    Either a boolean indicating if all event callbacks triggered the
    physics simulation should be enabled, or a list of strings
    indicating which ones should be used. If it's a list, you will
    need to specify one of the following events: `startStabilizing`,
    `stabilizationProgress`, `stabilizationIterationsDone`,
    `stabilized`. See
    https://visjs.github.io/vis-network/docs/network/#events for more
    details.

- findNode (dict; optional):
    Function call. Returns array of node ids showing in which clusters
    the desired node id exists in (if any).  Nodes can be in clusters.
    Clusters can also be in clusters.  This function returns and array
    of nodeIds showing where the node is. If any nodeId in the chain,
    especially the first passed in as a parameter, is not present in
    the current nodes list, an empty array is returned.  Example:
    cluster 'A' contains cluster 'B', cluster 'B' contains cluster
    'C', cluster 'C' contains node 'fred'.
    network.clustering.findNode('fred') will return
    ['A','B','C','fred'].

    `findNode` is a dict with keys:

    - nodeId (string | number; optional)

    - result (list of strings; optional)

- focus (dict; optional):
    Function call. You can focus on a node with this function. What
    that means is the view will lock onto that node, if it is moving,
    the view will also move accordingly. If the view is dragged by the
    user, the focus is broken. You can supply options to customize the
    effect: {   scale: Number,   offset: {x:Number, y:Number}
    locked: boolean   animation: { // -------------------> can be a
    boolean too!     duration: Number     easingFunction: String   } }
    All options except for locked are explained in the moveTo()
    description below. Locked denotes whether or not the view remains
    locked to the node once the zoom-in animation is finished. Default
    value is True. The options object is optional in the focus method.

    `focus` is a dict with keys:

    - nodeId (string; optional)

    - options (optional)

- getBaseEdges (dict; optional):
    Function call. For the given clusteredEdgeId, this method will
    return all the original base edge id's provided in data.edges. For
    a non-clustered (i.e. 'base') edge, clusteredEdgeId is returned.
    Only the base edge id's are returned. All clustered edges id's
    under clusteredEdgeId are skipped, but scanned recursively to
    return their base id's.

    `getBaseEdges` is a dict with keys:

    - clusteredEdgeId (string; optional)

    - result (list of strings; optional)

- getBoundingBox (dict; optional):
    Function call. Returns a bounding box for the node including label
    in the format: {   top: Number,   left: Number,   right: Number,
    bottom: Number } These values are in canvas space.

    `getBoundingBox` is a dict with keys:

    - nodeId (string; optional)

    - result (dict; optional)

- getClusteredEdges (dict; optional):
    Function call. Similar to findNode in that it returns all the edge
    ids that were created from the provided edge during clustering.
    Check the result property for results of this function call.

    `getClusteredEdges` is a dict with keys:

    - baseEdgeId (string; optional)

    - result (list of strings; optional)

- getConnectedEdges (dict; optional):
    Function call. Returns an array of edgeIds of the edges connected
    to this node.

    `getConnectedEdges` is a dict with keys:

    - nodeId (string; optional)

    - result (list of strings; optional)

- getConnectedNodes (dict; optional):
    Function call. Returns an array of nodeIds of all the nodes that
    are directly connected to this node or edge.  For a node id,
    returns an array with the id's of the connected nodes. If optional
    parameter direction is set to string 'from', only parent nodes are
    returned. If direction is set to 'to', only child nodes are
    returned. Any other value or undefined returns both parent and
    child nodes.  For an edge id, returns an array: [fromId, toId].
    Parameter direction is ignored for edges.

    `getConnectedNodes` is a dict with keys:

    - direction (string; optional)

    - nodeId (string; optional)

    - result (list of numbers; optional)

- getEdgeAt (dict; optional):
    Function call. Returns an edgeId or undefined. The DOM positions
    are expected to be in pixels from the top left corner of the
    canvas.

    `getEdgeAt` is a dict with keys:

    - position (dict; optional)

        `position` is a dict with keys:

        - x (number; optional)

        - y (number; optional)

    - result (list of strings; optional)

- getNodeAt (dict; optional):
    Function call. Returns a nodeId or undefined. The DOM positions
    are expected to be in pixels from the top left corner of the
    canvas.

    `getNodeAt` is a dict with keys:

    - position (dict; optional)

        `position` is a dict with keys:

        - x (number; optional)

        - y (number; optional)

    - result (list of strings; optional)

- getNodesInCluster (dict; optional):
    Function call. Returns an array of all nodeIds of the nodes that
    would be released if you open the cluster.

    `getNodesInCluster` is a dict with keys:

    - clusteredNodeId (string; optional)

    - result (list of strings; optional)

- getOptionsFromConfigurator (dict; optional):
    Function call. If you use the configurator, you can call this
    method to get an options object that contains all differences from
    the default options caused by users interacting with the
    configurator.

- getPosition (dict; optional):
    Function call. Returns the x y positions in canvas space of a
    specific node. network.getPosition('a123'); >   { x: 5, y: 12 }
    If no id is provided, the method will throw a TypeError If an id
    is provided that does not correspond to a node in the network, the
    method will throw a ReferenceError.

    `getPosition` is a dict with keys:

    - nodeId (string; optional)

    - result (dict; optional)

- getPositions (dict; optional):
    Function call. Returns the x y positions in canvas space of the
    nodes or node with the supplied nodeIds or nodeId as an object: //
    All nodes in the network. network.getPositions(); >   {
    a123: { x: 5, y: 12 },         b456: { x: 3, y: 4 },         c789:
    { x: 7, y: 10 }     }   // Specific nodes.
    network.getPositions(['a123', 'b456']); >   {         a123: { x:
    5, y: 12 },         b456: { x: 3, y: 4 },     }   // A single
    node. network.getPositions('a123'); >   {         a123: { x: 5, y:
    12 }     }   Alternative inputs are a string containing a nodeId
    or nothing. When a string is supplied, the position of the node
    corresponding to the id is returned in the same format. When
    nothing is supplied, the positions of all nodes are returned.
    Note: If a non-existent id is supplied, the method will return an
    empty object.

    `getPositions` is a dict with keys:

    - nodeIds (list; optional)

    - result (dict; optional)

- getScale (number; optional):
    Read-only property. Returns the current scale of the network. 1.0
    is comparable to 100%, 0 is zoomed out infinitely.

- getSeed (string | number; optional):
    Read-only prop. If you like the layout of your network and would
    like it to start in the same way next time, ask for the seed using
    this method and put it in the layout.randomSeed option.

- getSelectedEdges (list of string | numbers; optional):
    Read-only property. Returns an array of selected edge ids like so:
    [edgeId1, edgeId2, ..].

- getSelectedNodes (list of string | numbers; optional):
    Read-only property. Returns an array of selected node ids like so:
    [nodeId1, nodeId2, ..].

- getSelection (dict; optional):
    Read-only property. Returns an object with selected nodes and
    edges ids like this: {   nodes: [Array of selected nodeIds],
    edges: [Array of selected edgeIds] }.

- getViewPosition (dict; optional):
    Read-only property. Returns the current central focus point of the
    view in the form: { x: {Number}, y: {Number} }.

    `getViewPosition` is a dict with keys:

    - x (number; optional)

    - y (number; optional)

- hidePopup (number; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the popup (tooltip) is hidden. Returns
    none.

- hold (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type.    Fired when the user clicks and holds the mouse
    or taps and holds on a touchscreen device.    A click event is
    also fired in this case.

- hoverEdge (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired if the option interaction:{hover:True} is
    enabled and the mouse hovers over an edge.

- hoverNode (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired if the option interaction:{hover:True} is
    enabled and the mouse hovers over a node.

- initRedraw (dict; optional):
    Read-only prop. To use this, make sure that `enableOtherEvents` is
    set to `True`, or that `enableOtherEvents` is a list that contains
    this event type. Fired before the redrawing begins. The simulation
    step has completed at this point. Can be used to move custom
    elements before starting drawing the new frame.

- isCluster (dict; optional):
    Function call. Returns True if the node whose ID has been supplied
    is a cluster.

    `isCluster` is a dict with keys:

    - nodeId (string; optional)

    - result (boolean; optional)

- moveNode (dict; optional):
    Function call. You can use this to programmatically move a node.
    The supplied x and y positions have to be in canvas space!.

    `moveNode` is a dict with keys:

    - nodeId (string; optional)

    - x (number; optional)

    - y (number; optional)

- moveTo (dict; optional):
    Function call. You can animate or move the camera using the moveTo
    method. Options are: {   position: {x:Number, y:Number},   scale:
    Number,   offset: {x:Number, y:Number}   animation: { //
    -------------------> can be a boolean too!     duration: Number
    easingFunction: String   } } The position (in canvas units!) is
    the position of the central focus point of the camera. The scale
    is the target zoomlevel. Default value is 1.0. The offset (in DOM
    units) is how many pixels from the center the view is focussed.
    Default value is {x:0,y:0}. For animation you can either use a
    Boolean to use it with the default options or disable it or you
    can define the duration (in milliseconds) and easing function
    manually. Available are: linear, easeInQuad, easeOutQuad,
    easeInOutQuad, easeInCubic, easeOutCubic, easeInOutCubic,
    easeInQuart, easeOutQuart, easeInOutQuart, easeInQuint,
    easeOutQuint, easeInOutQuint. You will have to define at least a
    scale, position or offset. Otherwise, there is nothing to move to.

    `moveTo` is a dict with keys:

    - options (optional)

- off (dict; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Remove an event
    listener. The function you supply has to be the exact same as the
    one you used in the on function. If no function is supplied, all
    listeners will be removed. Look at the event section of the
    documentation for more information. Returns: None.

    `off` is a dict with keys:

    - callback (string; optional)

    - event_name (string; optional)

- on (dict; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Set an event
    listener. Depending on the type of event you get different
    parameters for the callback function. Look at the event section of
    the documentation for more information. callback must contain a
    valid javascript function Returns: None.

    `on` is a dict with keys:

    - callback (string; optional)

    - event_name (string; optional)

- once (dict; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Set an event
    listener only once. After it has taken place, the event listener
    will be removed. Depending on the type of event you get different
    parameters for the callback function. Look at the event section of
    the documentation for more information. Returns: None.

    `once` is a dict with keys:

    - callback (string; optional)

    - event_name (string; optional)

- oncontext (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type.    Fired when the user click on the canvas with
    the right mouse button.    The right mouse button does not select
    by default.    You can use the method getNodeAt to select the node
    if you want.

- openCluster (dict; optional):
    Function call. Opens the cluster, releases the contained nodes and
    edges, removing the cluster node and cluster edges. The options
    object is optional and currently supports one option,
    releaseFunction, which is a function that can be used to manually
    position the nodes after the cluster is opened. function
    releaseFunction (clusterPosition, containedNodesPositions) {
    var newPositions = {};     // clusterPosition = {x:clusterX,
    y:clusterY};     // containedNodesPositions =
    {nodeId:{x:nodeX,y:nodeY}, nodeId2....}     newPositions[nodeId] =
    {x:newPosX, y:newPosY};     return newPositions; } The
    containedNodesPositions contain the positions of the nodes in the
    cluster at the moment they were clustered. This function is
    expected to return the newPositions, which can be the
    containedNodesPositions (altered) or a new object. This has to be
    an object with keys equal to the nodeIds that exist in the
    containedNodesPositions and an {x:x,y:y} position object.  For all
    nodeIds not listed in this returned object, we will position them
    at the location of the cluster. This is also the default behaviour
    when no releaseFunction is defined.

    `openCluster` is a dict with keys:

    - nodeId (string; optional)

    - options (dict; optional)

- options (dict; optional):
    A graph configuration object. Pass a dict set according to your
    preferences / usecase as per the vis.js documentation. In Dash,
    this property also replaces vis.js setOptions function. See
    https://visjs.github.io/vis-network/docs/network/#options.

- redraw (boolean; default False):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Redraw the network.
    Returns: None.

- release (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired after drawing on the canvas has been
    completed. Can be used to draw on top of the network.

- releaseNode (boolean; optional):
    Function call. Programmatically release the focussed node.

- resize (dict; optional):
    Read-only prop. To use this, make sure that `enableOtherEvents` is
    set to `True`, or that `enableOtherEvents` is a list that contains
    this event type. Fired when the size of the canvas has been
    resized, either by a redraw call when the container div has
    changed in size, a setSize() call with new values or a
    setOptions() with new width and/or height values. Passes an object
    with properties structured as: {   width: Number     // the new
    width  of the canvas   height: Number    // the new height of the
    canvas   oldWidth: Number  // the old width  of the canvas
    oldHeight: Number // the old height of the canvas }.

- select (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Contains a list of selected nodes and edges.
    Struct is updated when a click, double click, context click, hold
    and release is performed on the graph.

- selectEdge (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when an edge has been selected by the user.

- selectEdges (dict; optional):
    Function call. Selects the edges corresponding to the id's in the
    input array. This method unselects all other objects before
    selecting its own objects. Does not fire events.

    `selectEdges` is a dict with keys:

    - edgeIds (list; optional)

- selectNode (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when a node has been selected by the user.

- selectNodes (dict; optional):
    Function call. Selects the nodes corresponding to the id's in the
    input array. If highlightEdges is True or undefined, the
    neighbouring edges will also be selected. This method unselects
    all other objects before selecting its own objects. Does not fire
    events.

    `selectNodes` is a dict with keys:

    - highlightEdges (boolean; optional)

    - nodeIds (list; optional)

- setSelection (dict; optional):
    Function call. Sets the selection, wich must be an object like
    this: {   nodes: [Array of nodeIds],   edges: [Array of edgeIds] }
    You can also pass only nodes or edges in selection object.
    Available options are: {   unselectAll: Boolean,   highlightEdges:
    Boolean }.

    `setSelection` is a dict with keys:

    - options (dict; optional)

        `options` is a dict with keys:

        - highlightEdges (boolean; optional)

        - unselectAll (boolean; optional)

    - selection (dict; optional)

        `selection` is a dict with keys:

        - edges (list of strings; optional)

        - nodes (list of strings; optional)

- setSize (dict; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. Set the size of the
    canvas. This is automatically done on a window resize. Returns:
    None.

    `setSize` is a dict with keys:

    - height (string; optional)

    - width (string; optional)

- showPopup (number; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the popup (tooltip) is shown. Returns
    id of item corresponding to popup.

- stabilizationIterationsDone (boolean | number | string | dict | list; optional):
    Read-only prop. To use this, make sure that `enablePhysicsEvents`
    is set to `True`, or that `enablePhysicsEvents` is a list that
    contains this event type. Fired when the 'hidden' stabilization
    finishes. This does not necessarily mean the network is
    stabilized; it could also mean that the amount of iterations
    defined in the options has been reached.

- stabilizationProgress (dict; optional):
    Read-only prop. To use this, make sure that `enablePhysicsEvents`
    is set to `True`, or that `enablePhysicsEvents` is a list that
    contains this event type. Fired when a multiple of the
    updateInterval number of iterations is reached. This only occurs
    in the 'hidden' stabilization. Passes an object with properties
    structured as: {   iterations: Number // iterations so far,
    total: Number      // total iterations in options }.

- stabilize (number; optional):
    Function call. You can manually call stabilize at any time. All
    the stabilization options above are used. You can optionally
    supply the number of iterations it should do.

- stabilized (dict; optional):
    Read-only prop. To use this, make sure that `enablePhysicsEvents`
    is set to `True`, or that `enablePhysicsEvents` is a list that
    contains this event type. Fired when the network has stabilized or
    when the stopSimulation() has been called. The amount of
    iterations it took could be used to tweak the maximum amount of
    iterations needed to stabilize the network. Passes an object with
    properties structured as: {   iterations: Number // iterations it
    took }.

- startSimulation (boolean; optional):
    Function call. Start the physics simulation. This is normally done
    whenever needed and is only really useful if you stop the
    simulation yourself and wish to continue it afterwards.

- startStabilizing (boolean | number | string | dict | list; optional):
    Read-only prop. To use this, make sure that `enablePhysicsEvents`
    is set to `True`, or that `enablePhysicsEvents` is a list that
    contains this event type. Fired when stabilization starts. This is
    also the case when you drag a node and the physics simulation
    restarts to stabilize again. Stabilization does not necessarily
    imply 'without showing'.

- stopSimulation (boolean; optional):
    Function call. Returns a bounding box for the node including label
    in the format: {   top: Number,   left: Number,   right: Number,
    bottom: Number } These values are in canvas space.

- storePositions (boolean; optional):
    Write-only property. Pass True value to this property as an output
    to call the underlying function on the graph. When using the
    vis.DataSet to load your nodes into the network, this method will
    put the X and Y positions of all nodes into that dataset. If
    you're loading your nodes from a database and have this
    dynamically coupled with the DataSet, you can use this to
    stabilize your network once, then save the positions in that
    database through the DataSet so the next time you load the nodes,
    stabilization will be near instantaneous.  If the nodes are still
    moving and you're using dynamic smooth edges (which is on by
    default), you can use the option stabilization.onlyDynamicEdges in
    the physics module to improve initialization time.  This method
    does not support clustering. At the moment it is not possible to
    cache positions when using clusters since they cannot be correctly
    initialized from just the positions.  moveNode(nodeId, Number x,
    Number y)  getBoundingBox(String nodeId)  getConnectedNodes(String
    nodeId or edgeId, [String direction])  getConnectedEdges(String
    nodeId) Returns: None.

- style (dict; optional):
    Defines CSS styles which will override styles previously set.

- unselectAll (boolean; optional):
    Function call. Unselect all objects. Does not fire events.

- updateClusteredNode (dict; optional):
    Function call. Returns nothing. Visible edges between clustered
    nodes are not the same edge as the ones provided in data.edges
    passed on network creation With each layer of clustering, copies
    of the edges between clusters are created and the previous edges
    are hidden, until the cluster is opened. This method takes an
    edgeId (ie. a base edgeId from data.edges) and applies the options
    to it and any edges that were created from it while clustering.
    Example: network.clustering.updateEdge(originalEdge.id, {color :
    '#aa0000'}); This would turn the base edge and any subsequent
    edges red, so when opening clusters the edges will all be the same
    color.

    `updateClusteredNode` is a dict with keys:

    - clusteredNodeId (string; optional)

    - options (dict; optional)

- updateEdge (dict; optional):
    Function call. Returns nothing. Visible edges between clustered
    nodes are not the same edge as the ones provided in data.edges
    passed on network creation With each layer of clustering, copies
    of the edges between clusters are created and the previous edges
    are hidden, until the cluster is opened. This method takes an
    edgeId (ie. a base edgeId from data.edges) and applies the options
    to it and any edges that were created from it while clustering.
    Example: network.clustering.updateEdge(originalEdge.id, {color :
    '#aa0000'}); This would turn the base edge and any subsequent
    edges red, so when opening clusters the edges will all be the same
    color.

    `updateEdge` is a dict with keys:

    - options (dict; optional)

    - startEdgeId (string; optional)

- zoom (dict; optional):
    Read-only prop. To use this, make sure that `enableHciEvents` is
    set to `True`, or that `enableHciEvents` is a list that contains
    this event type. Fired when the user zooms in or out. The
    properties tell you which direction the zoom is in. The scale is a
    number greater than 0, which is the same that you get with
    network.getScale(). When fired by clicking the zoom in or zoom out
    navigation buttons, the pointer property of the object passed will
    be None. Passes an object with properties structured as: {
    direction: '+'/'-',   scale: Number,   pointer: {x:pointer_x,
    y:pointer_y} }."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dashvis'
    _type = 'DashNetwork'
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, data=Component.UNDEFINED, options=Component.UNDEFINED, style=Component.UNDEFINED, enableHciEvents=Component.UNDEFINED, click=Component.UNDEFINED, doubleClick=Component.UNDEFINED, oncontext=Component.UNDEFINED, hold=Component.UNDEFINED, release=Component.UNDEFINED, select=Component.UNDEFINED, selectNode=Component.UNDEFINED, selectEdge=Component.UNDEFINED, deselectNode=Component.UNDEFINED, deselectEdge=Component.UNDEFINED, dragStart=Component.UNDEFINED, dragging=Component.UNDEFINED, dragEnd=Component.UNDEFINED, controlNodeDragging=Component.UNDEFINED, controlNodeDragEnd=Component.UNDEFINED, hoverNode=Component.UNDEFINED, blurNode=Component.UNDEFINED, hoverEdge=Component.UNDEFINED, blurEdge=Component.UNDEFINED, zoom=Component.UNDEFINED, showPopup=Component.UNDEFINED, hidePopup=Component.UNDEFINED, enablePhysicsEvents=Component.UNDEFINED, startStabilizing=Component.UNDEFINED, stabilizationProgress=Component.UNDEFINED, stabilizationIterationsDone=Component.UNDEFINED, stabilized=Component.UNDEFINED, enableOtherEvents=Component.UNDEFINED, resize=Component.UNDEFINED, initRedraw=Component.UNDEFINED, beforeDrawing=Component.UNDEFINED, afterDrawing=Component.UNDEFINED, animationFinished=Component.UNDEFINED, configChange=Component.UNDEFINED, destroy=Component.UNDEFINED, on=Component.UNDEFINED, off=Component.UNDEFINED, once=Component.UNDEFINED, canvasToDOM=Component.UNDEFINED, DOMtoCanvas=Component.UNDEFINED, redraw=Component.UNDEFINED, setSize=Component.UNDEFINED, cluster=Component.UNDEFINED, clusterByConnection=Component.UNDEFINED, clusterByHubsize=Component.UNDEFINED, clusterOutliers=Component.UNDEFINED, findNode=Component.UNDEFINED, getClusteredEdges=Component.UNDEFINED, getBaseEdges=Component.UNDEFINED, updateEdge=Component.UNDEFINED, updateClusteredNode=Component.UNDEFINED, isCluster=Component.UNDEFINED, getNodesInCluster=Component.UNDEFINED, openCluster=Component.UNDEFINED, getSeed=Component.UNDEFINED, enableEditMode=Component.UNDEFINED, disableEditMode=Component.UNDEFINED, addNodeMode=Component.UNDEFINED, editNode=Component.UNDEFINED, addEdgeMode=Component.UNDEFINED, editEdgeMode=Component.UNDEFINED, deleteSelected=Component.UNDEFINED, getPositions=Component.UNDEFINED, getPosition=Component.UNDEFINED, storePositions=Component.UNDEFINED, moveNode=Component.UNDEFINED, getBoundingBox=Component.UNDEFINED, getConnectedNodes=Component.UNDEFINED, getConnectedEdges=Component.UNDEFINED, startSimulation=Component.UNDEFINED, stopSimulation=Component.UNDEFINED, stabilize=Component.UNDEFINED, getSelection=Component.UNDEFINED, getSelectedNodes=Component.UNDEFINED, getSelectedEdges=Component.UNDEFINED, getNodeAt=Component.UNDEFINED, getEdgeAt=Component.UNDEFINED, selectNodes=Component.UNDEFINED, selectEdges=Component.UNDEFINED, setSelection=Component.UNDEFINED, unselectAll=Component.UNDEFINED, getScale=Component.UNDEFINED, getViewPosition=Component.UNDEFINED, focus=Component.UNDEFINED, moveTo=Component.UNDEFINED, releaseNode=Component.UNDEFINED, getOptionsFromConfigurator=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'DOMtoCanvas', 'addEdgeMode', 'addNodeMode', 'afterDrawing', 'animationFinished', 'beforeDrawing', 'blurEdge', 'blurNode', 'canvasToDOM', 'click', 'cluster', 'clusterByConnection', 'clusterByHubsize', 'clusterOutliers', 'configChange', 'controlNodeDragEnd', 'controlNodeDragging', 'data', 'deleteSelected', 'deselectEdge', 'deselectNode', 'destroy', 'disableEditMode', 'doubleClick', 'dragEnd', 'dragStart', 'dragging', 'editEdgeMode', 'editNode', 'enableEditMode', 'enableHciEvents', 'enableOtherEvents', 'enablePhysicsEvents', 'findNode', 'focus', 'getBaseEdges', 'getBoundingBox', 'getClusteredEdges', 'getConnectedEdges', 'getConnectedNodes', 'getEdgeAt', 'getNodeAt', 'getNodesInCluster', 'getOptionsFromConfigurator', 'getPosition', 'getPositions', 'getScale', 'getSeed', 'getSelectedEdges', 'getSelectedNodes', 'getSelection', 'getViewPosition', 'hidePopup', 'hold', 'hoverEdge', 'hoverNode', 'initRedraw', 'isCluster', 'moveNode', 'moveTo', 'off', 'on', 'once', 'oncontext', 'openCluster', 'options', 'redraw', 'release', 'releaseNode', 'resize', 'select', 'selectEdge', 'selectEdges', 'selectNode', 'selectNodes', 'setSelection', 'setSize', 'showPopup', 'stabilizationIterationsDone', 'stabilizationProgress', 'stabilize', 'stabilized', 'startSimulation', 'startStabilizing', 'stopSimulation', 'storePositions', 'style', 'unselectAll', 'updateClusteredNode', 'updateEdge', 'zoom']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'DOMtoCanvas', 'addEdgeMode', 'addNodeMode', 'afterDrawing', 'animationFinished', 'beforeDrawing', 'blurEdge', 'blurNode', 'canvasToDOM', 'click', 'cluster', 'clusterByConnection', 'clusterByHubsize', 'clusterOutliers', 'configChange', 'controlNodeDragEnd', 'controlNodeDragging', 'data', 'deleteSelected', 'deselectEdge', 'deselectNode', 'destroy', 'disableEditMode', 'doubleClick', 'dragEnd', 'dragStart', 'dragging', 'editEdgeMode', 'editNode', 'enableEditMode', 'enableHciEvents', 'enableOtherEvents', 'enablePhysicsEvents', 'findNode', 'focus', 'getBaseEdges', 'getBoundingBox', 'getClusteredEdges', 'getConnectedEdges', 'getConnectedNodes', 'getEdgeAt', 'getNodeAt', 'getNodesInCluster', 'getOptionsFromConfigurator', 'getPosition', 'getPositions', 'getScale', 'getSeed', 'getSelectedEdges', 'getSelectedNodes', 'getSelection', 'getViewPosition', 'hidePopup', 'hold', 'hoverEdge', 'hoverNode', 'initRedraw', 'isCluster', 'moveNode', 'moveTo', 'off', 'on', 'once', 'oncontext', 'openCluster', 'options', 'redraw', 'release', 'releaseNode', 'resize', 'select', 'selectEdge', 'selectEdges', 'selectNode', 'selectNodes', 'setSelection', 'setSize', 'showPopup', 'stabilizationIterationsDone', 'stabilizationProgress', 'stabilize', 'stabilized', 'startSimulation', 'startStabilizing', 'stopSimulation', 'storePositions', 'style', 'unselectAll', 'updateClusteredNode', 'updateEdge', 'zoom']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashNetwork, self).__init__(**args)
