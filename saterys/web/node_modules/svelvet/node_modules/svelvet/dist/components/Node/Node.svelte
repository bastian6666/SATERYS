<script context="module">import InternalNode from "./InternalNode.svelte";
import DefaultNode from "./DefaultNode.svelte";
import { get } from "svelte/store";
import { createNode } from "../../utils";
import { getContext, onDestroy, onMount, setContext } from "svelte";
</script>

<script>const graph = getContext("graph");
const group = getContext("group");
export let position = { x: 0, y: 0 };
export let drop = false;
export let dimensions = null;
export let id = 0;
export let bgColor = null;
export let borderRadius = null;
export let borderColor = null;
export let borderWidth = null;
export let selectionColor = null;
export let textColor = null;
export let resizable = false;
export let label = "";
export let inputs = 1;
export let outputs = 1;
export let width = null;
export let height = null;
export let TD = false;
export let LR = false;
export let zIndex = 1;
export let editable = true;
export let locked = false;
export let rotation = 0;
export let edge = null;
export let connections = [];
export let useDefaults = false;
export let center = false;
export let dynamic = false;
export let title = "";
const nodes = graph.nodes;
setContext("dynamic", dynamic);
let node;
let isDefault = true;
onMount(() => {
  const direction = TD ? "TD" : LR ? "LR" : graph.direction;
  const groupBox = graph.groupBoxes.get(group);
  const nodeCount = graph.nodes.count() + 1;
  isDefault = !$$slots.default;
  if ($$slots.anchorWest || $$slots.anchorEast || $$slots.anchorNorth || $$slots.anchorSouth)
    isDefault = false;
  const initialDimensions = dimensions ? dimensions : width || height ? { width: width || height || 200, height: height || width || 100 } : isDefault ? { width: 200, height: 100 } : { width: 0, height: 0 };
  const config = {
    id: id || nodeCount,
    position: drop === "cursor" ? { x: get(graph.cursor).x, y: get(graph.cursor).y } : groupBox ? { x: get(groupBox.position).x + position.x, y: get(groupBox.position).y + position.y } : position,
    dimensions: initialDimensions,
    editable: editable || graph.editable,
    label,
    group,
    resizable,
    inputs,
    outputs,
    zIndex,
    direction,
    locked,
    rotation
  };
  if (connections.length)
    config.connections = connections;
  if (borderWidth)
    config.borderWidth = borderWidth;
  if (borderRadius)
    config.borderRadius = borderRadius;
  if (borderColor)
    config.borderColor = borderColor;
  if (selectionColor)
    config.selectionColor = selectionColor;
  if (textColor)
    config.textColor = textColor;
  if (bgColor)
    config.bgColor = bgColor;
  if (edge)
    config.edge = edge;
  node = createNode(config);
  if (groupBox) {
    graph.groups.update((groups) => {
      const nodes2 = get(groups[group].nodes);
      groups[group].nodes.set(/* @__PURE__ */ new Set([...nodes2, node]));
      return groups;
    });
  }
  graph.nodes.add(node, node.id);
});
$:
  node && node.connections.set(connections);
onDestroy(() => {
  graph.nodes.delete(node.id);
});
function connect(connections2) {
  if (!node)
    return;
  node.connections.set([connections2]);
}
function disconnect(connections2) {
  if (!node)
    return;
  const adjustedConnections = Array.isArray(connections2) ? connections2 : [connections2];
  adjustedConnections.forEach((connection) => {
    const [nodeId, anchorId] = Array.isArray(connection) ? connection : [connection, null];
    const nodeKey = `N-${nodeId}`;
    const otherNode = graph.nodes.get(nodeKey);
    if (!otherNode)
      return;
    let specificAnchor = null;
    const anchorKey = anchorId ? `A-${anchorId}/${nodeKey}` : null;
    if (anchorKey) {
      specificAnchor = otherNode.anchors.get(anchorKey);
    }
    const matchingEdgeKeys = graph.edges.match(node, otherNode, specificAnchor);
    if (matchingEdgeKeys.length)
      graph.edges.delete(matchingEdgeKeys[matchingEdgeKeys.length - 1]);
  });
}
setContext("connect", connect);
setContext("disconnect", disconnect);
$:
  if (node) {
    node.bgColor.set(bgColor);
  }
$:
  if (node) {
    node.label.set(label);
  }
$:
  if (node) {
    node.textColor.set(textColor);
  }
$:
  if (node) {
    node.borderColor.set(borderColor);
  }
$:
  if (node) {
    node.selectionColor.set(selectionColor);
  }
$:
  if (node) {
    node.resizable.set(resizable);
  }
$:
  if (node) {
    node.editable.set(editable);
  }
$:
  if (node) {
    node.locked.set(locked);
  }
$:
  if (node) {
    node.inputs.set(inputs);
  }
$:
  if (node) {
    node.outputs.set(outputs);
  }
$:
  if (node) {
    node.zIndex.set(zIndex);
  }
$:
  nodePosition = node && node?.position;
let priorPosition = position;
$:
  if (node) {
    const { x: priorX, y: priorY } = priorPosition;
    const { x: nodeX, y: nodeY } = $nodePosition;
    const { x: propX, y: propY } = position;
    const areDifferent = propX !== nodeX || propY !== nodeY;
    const propChanged = propX !== priorX || propY !== priorY;
    if (areDifferent) {
      if (propChanged) {
        priorPosition = position;
        node.position.set(position);
      } else {
        priorPosition = $nodePosition;
        position = $nodePosition;
      }
    }
  }
$:
  if (node) {
    node.inputs.set(inputs);
  }
$:
  if (node) {
    node.outputs.set(outputs);
  }
</script>

{#if node && $nodes.get(node.id)}
	<InternalNode
		{node}
		center={center || drop === 'center'}
		{isDefault}
		{useDefaults}
		dimensionsProvided={!!dimensions || !!width || !!height || isDefault || false}
		nodeStore={graph.nodes}
		locked={graph.locked}
		groups={graph.groups}
		{title}
		maxZIndex={graph.maxZIndex}
		centerPoint={graph.center}
		cursor={graph.cursor}
		activeGroup={graph.activeGroup}
		editing={graph.editing}
		initialNodePositions={graph.initialNodePositions}
		on:nodeClicked
		on:nodeMount
		on:nodeReleased
		on:duplicate
		let:destroy
		let:selected
		let:grabHandle
	>
		<slot {selected} {grabHandle} {disconnect} {connect} {node} {destroy}>
			{#if isDefault}
				<DefaultNode {selected} on:connection on:disconnection />
			{/if}
		</slot>

		<slot name="anchorWest" slot="anchorWest" />
		<slot name="anchorEast" slot="anchorEast" />
		<slot name="anchorNorth" slot="anchorNorth" />
		<slot name="anchorSouth" slot="anchorSouth" />
	</InternalNode>
{/if}
