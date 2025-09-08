<script context="module">import DefaultAnchor from "./DefaultAnchor.svelte";
import Edge from "../Edge/Edge.svelte";
import EdgeContext from "../Edge/EdgeContext.svelte";
import { onMount, getContext, onDestroy, afterUpdate } from "svelte";
import { writable, get } from "svelte/store";
import { createEdge, createAnchor, generateOutput } from "../../utils/creators";
import { createEventDispatcher } from "svelte";
let animationFrameId;
export const connectingFrom = writable(null);
export function changeAnchorSide(anchorElement, newSide, node) {
  if (newSide === "self")
    return;
  const parentNode = anchorElement.parentNode;
  if (!parentNode)
    return;
  parentNode.removeChild(anchorElement);
  const newContainer = document.querySelector(`#anchors-${newSide}-${node.id}`);
  if (!newContainer)
    return;
  newContainer.appendChild(anchorElement);
  if (anchorElement)
    node.recalculateAnchors();
}
</script>

<script>const nodeDynamic = getContext("dynamic");
const node = getContext("node");
const edgeStore = getContext("edgeStore");
const cursorAnchor = getContext("cursorAnchor");
const graphDirection = getContext("direction");
const mounted = getContext("mounted");
const graph = getContext("graph");
const nodeStore = getContext("nodeStore");
const graphEdge = getContext("graphEdge");
const nodeConnectEvent = getContext("nodeConnectEvent");
const anchorsMounted = getContext("anchorsMounted");
const flowChart = getContext("flowchart") || void 0;
export let bgColor = null;
export let id = 0;
export let input = false;
export let output = false;
export let multiple = output ? true : input ? false : true;
export let dynamic = nodeDynamic || false;
export let edge = null;
export let inputsStore = null;
export let key = null;
export let outputStore = null;
export let connections = [];
export let edgeColor = writable(null);
export let edgeLabel = "";
export let locked = false;
export let nodeConnect = false;
export let edgeStyle = null;
export let endStyles = [null, null];
export let invisible = false;
export let direction = graphDirection === "TD" ? input ? "north" : "south" : input ? "west" : "east";
export let title = "";
const dispatchConnection = createEventDispatcher();
const dispatchDisconnection = createEventDispatcher();
let anchorElement;
let tracking = false;
let hovering = false;
let previousConnectionCount = 0;
let type = input === output ? null : input ? "input" : "output";
let assignedConnections = [];
const nodeEdge = node.edge;
const anchors = node.anchors;
const resizingWidth = node.resizingWidth;
const resizingHeight = node.resizingHeight;
const rotating = node.rotating;
const nodeLevelConnections = node.connections;
$:
  connecting = $connectingFrom?.anchor === anchor;
$:
  connectedAnchors = anchor && anchor.connected;
const anchorKey = `A-${id || anchors.count() + 1}/${node.id}`;
const anchor = createAnchor(
  graph,
  node,
  anchorKey,
  { x: 0, y: 0 },
  { width: 0, height: 0 },
  inputsStore || outputStore || null,
  edge || nodeEdge || graphEdge || null,
  type,
  direction,
  dynamic,
  key,
  edgeColor
);
anchors.add(anchor, anchor.id);
onMount(() => {
  if (anchorElement)
    anchor.recalculatePosition();
  const outputCount = Array.from(get(node.anchors)).reduce((acc, [, anchor2]) => {
    if (anchor2.type === "output")
      acc++;
    return acc;
  }, 0);
  if ($nodeLevelConnections?.length && !input) {
    const remainingConnections = [];
    let first = null;
    $nodeLevelConnections.forEach((connection, i) => {
      if (!connection)
        return;
      if (first === null)
        first = i;
      if ((i - first) % outputCount === 0) {
        assignedConnections.push(connection);
        remainingConnections.push(null);
      } else {
        remainingConnections.push(connection);
      }
    });
    $nodeLevelConnections = remainingConnections;
  }
  $anchorsMounted++;
});
afterUpdate(() => {
  if (anchorElement)
    anchor.recalculatePosition();
});
onDestroy(() => {
  destroy();
  cancelAnimationFrame(animationFrameId);
});
$:
  dynamicDirection = anchor?.direction;
$:
  if (dynamic && anchorElement)
    changeAnchorSide(anchorElement, $dynamicDirection, node);
$:
  if ($mounted === nodeStore.count() && connections.length) {
    checkDirectConnections();
  }
$:
  if (nodeConnect && $nodeConnectEvent) {
    handleMouseUp($nodeConnectEvent);
  }
$:
  if ($mounted === nodeStore.count() && assignedConnections.length) {
    checkNodeLevelConnections();
  }
$:
  if (anchorElement) {
    $anchors;
    $connectedAnchors;
    $dynamicDirection;
    anchor.recalculatePosition();
  }
$:
  if (!tracking && ($resizingWidth || $resizingHeight || $rotating)) {
    tracking = true;
    trackPosition();
  } else if (!$resizingWidth && !$resizingHeight && tracking && !$rotating) {
    tracking = false;
    cancelAnimationFrame(animationFrameId);
  }
$:
  if ($connectedAnchors) {
    if ($connectedAnchors.size < previousConnectionCount) {
      dispatchDisconnection("disconnection", { node, anchor });
    } else if ($connectedAnchors.size > previousConnectionCount) {
      const anchorArray = Array.from($connectedAnchors);
      const lastConnection = anchorArray[anchorArray.length - 1];
      dispatchConnection("connection", {
        node,
        anchor,
        connectedNode: lastConnection.node,
        connectedAnchor: lastConnection
      });
    }
    previousConnectionCount = $connectedAnchors.size;
  }
function touchBasedConnection(e) {
  edgeStore.delete("cursor");
  const touchPosition = {
    x: e.changedTouches[0].clientX,
    y: e.changedTouches[0].clientY
  };
  const otherAnchor = document.elementFromPoint(touchPosition.x, touchPosition.y);
  if (!otherAnchor)
    return;
  const parentElement = otherAnchor.parentElement;
  if (!parentElement)
    return;
  const compoundId = parentElement.id;
  const nodeId = compoundId.split("/")[1];
  const connectingAnchor = nodeStore.get(nodeId)?.anchors.get(compoundId);
  if (!connectingAnchor)
    return;
  edgeStore.delete("cursor");
  attemptConnection(anchor, connectingAnchor, e);
}
function attemptConnection(source, target, e) {
  const success = connectAnchors(source, target);
  if (success) {
    connectStores();
  }
  if (!e.shiftKey) {
    clearLinking(success);
  }
}
function handleMouseUp(e) {
  if ("changedTouches" in e && connecting) {
    touchBasedConnection(e);
    return;
  }
  if (connecting)
    return;
  if ($connectedAnchors?.size && !multiple) {
    edgeStore.delete("cursor");
    if (!e.shiftKey)
      clearLinking(false);
    return;
  }
  if ($connectingFrom)
    connectEdge(e);
}
function handleClick(e) {
  if (locked)
    return;
  if ($connectedAnchors?.size && !multiple && !$connectingFrom)
    return disconnectEdge();
  if (!$connectingFrom)
    return startEdge();
  connectEdge(e);
}
function startEdge() {
  if (input === output) {
    $connectingFrom = { anchor, store: null, key: null };
    createCursorEdge(anchor, cursorAnchor);
  } else if (input) {
    $connectingFrom = {
      anchor,
      store: inputsStore,
      key
    };
    createCursorEdge(cursorAnchor, anchor);
  } else if (output) {
    $connectingFrom = {
      anchor,
      store: outputStore,
      key: null
    };
    createCursorEdge(anchor, cursorAnchor);
  }
}
function createCursorEdge(source, target, disconnect2 = false) {
  const edgeConfig = {
    color: edgeColor,
    label: { text: edgeLabel }
  };
  if (disconnect2)
    edgeConfig.disconnect = true;
  if (edgeStyle)
    edgeConfig.type = edgeStyle;
  if (endStyles[0])
    edgeConfig.start = endStyles[0];
  if (endStyles[1])
    edgeConfig.start = endStyles[1];
  const newEdge = createEdge({ source, target }, source?.edge || null, edgeConfig);
  edgeStore.add(newEdge, "cursor");
}
function connectEdge(e) {
  edgeStore.delete("cursor");
  if (!$connectingFrom)
    return;
  const connectingType = $connectingFrom.anchor.type;
  if ($connectingFrom.anchor === anchor || connectingType === anchor.type && connectingType) {
    clearLinking(false);
    return;
  }
  anchor.recalculatePosition();
  let source;
  let target;
  if (input === output) {
    if (connectingType === "input") {
      source = anchor;
      target = $connectingFrom.anchor;
    } else {
      source = $connectingFrom.anchor;
      target = anchor;
    }
  } else if (input) {
    source = $connectingFrom.anchor;
    target = anchor;
  } else {
    source = anchor;
    target = $connectingFrom.anchor;
  }
  attemptConnection(source, target, e);
}
function connectAnchors(source, target) {
  if (source === target)
    return false;
  if (get(source.connected).has(anchor))
    return false;
  const edgeConfig = {
    color: edgeColor,
    label: { text: edgeLabel }
  };
  if (flowChart) {
    const sourceId = source.node.id.slice(2);
    const sourceInFlowchart = flowChart.nodeList[sourceId];
    if (sourceInFlowchart) {
      const targetId = target.node.id.slice(2);
      const targetInSourceChildren = sourceInFlowchart.children.filter(
        (child) => child.node.id === targetId
      )[0];
      if (targetInSourceChildren) {
        const edgeData = targetInSourceChildren;
        edgeConfig.label = { text: edgeData.content };
      }
    }
  }
  if (edgeStyle)
    edgeConfig.type = edgeStyle;
  if (endStyles[0])
    edgeConfig.start = endStyles[0];
  if (endStyles[1])
    edgeConfig.start = endStyles[1];
  const newEdge = createEdge({ source, target }, source?.edge || null, edgeConfig);
  if (!source.node || !target.node)
    return false;
  edgeStore.add(newEdge, /* @__PURE__ */ new Set([source, target, source.node, target.node]));
  return true;
}
function connectStores() {
  if (input && $connectingFrom && $connectingFrom.store) {
    if ($inputsStore && key && inputsStore && typeof inputsStore.set === "function" && typeof inputsStore.update === "function")
      $inputsStore[key] = $connectingFrom.store;
  } else if (output && $connectingFrom && $connectingFrom.store) {
    const { store, key: key2 } = $connectingFrom;
    if (store && key2 && typeof store.update === "function")
      store.update((store2) => {
        if (!outputStore)
          return store2;
        store2[key2] = outputStore;
        return store2;
      });
  }
}
function disconnectStore() {
  if ($inputsStore && key && $inputsStore[key])
    $inputsStore[key] = writable(get($inputsStore[key]));
}
function clearLinking(connectionMade) {
  if (connectionMade || !$nodeConnectEvent) {
    $connectingFrom = null;
    $nodeConnectEvent = null;
  }
}
function trackPosition() {
  if (!tracking)
    return;
  if (anchorElement)
    anchor.recalculatePosition();
  animationFrameId = requestAnimationFrame(trackPosition);
}
function destroy() {
  edgeStore.delete("cursor");
  const connections2 = edgeStore.match(anchor);
  connections2.forEach((edge2) => edgeStore.delete(edge2));
  clearLinking(false);
  disconnectStore();
}
function disconnectEdge() {
  if (get(anchor.connected).size > 1)
    return;
  const source = Array.from(get(anchor.connected))[0];
  if (source.type === "input")
    return;
  destroy();
  if (source.type === "output") {
    createCursorEdge(source, cursorAnchor, true);
    disconnectStore();
    const store = source.store;
    $connectingFrom = { anchor: source, store, key: null };
  } else {
    createCursorEdge(source, cursorAnchor, true);
    $connectingFrom = { anchor: source, store: null, key: null };
  }
}
function checkNodeLevelConnections() {
  assignedConnections.forEach((connection, index) => {
    if (!connection)
      return;
    const connected = processConnection(connection);
    if (connected)
      connections[index] = null;
  });
  assignedConnections = assignedConnections.filter((connection) => connection !== null);
}
function checkDirectConnections() {
  connections.forEach((connection) => {
    if (!connection)
      return;
    processConnection(connection);
  });
}
export function disconnect(target) {
  const nodekey = `N-${target[0]}`;
  const node2 = nodeStore.get(nodekey);
  if (!node2)
    return;
  const targetAnchor = node2.anchors.get(`A-${target[1]}/N-${target[0]}`);
  if (!targetAnchor)
    return;
  const edgeKey = edgeStore.match(anchor, targetAnchor);
  if (!edgeKey)
    return;
  edgeStore.delete(edgeKey[0]);
}
const processConnection = (connection) => {
  let nodeId;
  let anchorId;
  let anchorToConnect = null;
  if (Array.isArray(connection)) {
    nodeId = connection[0].toString();
    anchorId = connection[1].toString();
  } else {
    nodeId = connection.toString();
    anchorId = null;
  }
  const nodekey = `N-${nodeId}`;
  const nodeToConnect = nodeStore.get(nodekey);
  if (!nodeToConnect) {
    return false;
  }
  if (!anchorId) {
    const anchorStore = get(nodeToConnect.anchors);
    const anchors2 = Array.from(anchorStore.values());
    if (!anchors2.length) {
      return false;
    }
    anchorToConnect = anchors2.reduce((a, b) => {
      if (!a && b.type === "output")
        return null;
      if (b.type === "output")
        return a;
      if (!a)
        return b;
      if (get(b.connected).size < get(a.connected).size)
        return b;
      return a;
    }, null);
  } else {
    const anchorKey2 = `A-${anchorId}/${nodekey}`;
    anchorToConnect = nodeToConnect.anchors.get(anchorKey2) || null;
  }
  if (!anchorToConnect) {
    return false;
  }
  connectAnchors(anchor, anchorToConnect);
  if (anchorToConnect.store && (inputsStore || outputStore)) {
    if (input && anchorToConnect.type === "output") {
      if ($inputsStore && key && inputsStore && typeof inputsStore.set === "function" && typeof inputsStore.update === "function")
        $inputsStore[key] = anchorToConnect.store;
    } else if (output && anchorToConnect.type === "input") {
      const { store, inputKey } = anchorToConnect;
      if (store && inputKey && typeof store.update === "function")
        store.update((store2) => {
          if (!outputStore)
            return store2;
          store2[inputKey] = outputStore;
          return store2;
        });
    }
  }
  return true;
};
</script>

<div
	id={anchor?.id}
	class="anchor-wrapper"
	role="button"
	tabindex="0"
	class:locked
	title={title || ''}
	on:mouseenter={() => (hovering = true)}
	on:mouseleave={() => (hovering = false)}
	on:mousedown|stopPropagation|preventDefault={handleClick}
	on:mouseup|stopPropagation={handleMouseUp}
	on:touchstart|stopPropagation|preventDefault={handleClick}
	on:touchend|stopPropagation={handleMouseUp}
	bind:this={anchorElement}
>
	<slot linked={$connectedAnchors?.size >= 1} {hovering} {connecting}>
		{#if !invisible}
			<DefaultAnchor
				{output}
				{input}
				{connecting}
				{hovering}
				{bgColor}
				connected={$connectedAnchors?.size >= 1}
			/>
		{/if}
	</slot>
</div>

{#each Array.from($connectedAnchors) as target (target.id)}
	{@const edge = edgeStore.fetch(anchor, target)}
	{#if edge && edge.source === anchor}
		{@const CustomEdge = edge.component}
		<EdgeContext {edge}>
			<slot name="edge">
				{#if CustomEdge}
					<CustomEdge />
				{:else}
					<Edge />
				{/if}
			</slot>
		</EdgeContext>
	{/if}
{/each}

{#if connecting}
	{@const edge = edgeStore.get('cursor')}
	{#if edge}
		{@const CustomEdge = edge.component}
		<EdgeContext {edge}>
			<slot name="edge">
				{#if CustomEdge}
					<CustomEdge />
				{:else}
					<Edge />
				{/if}
			</slot>
		</EdgeContext>
	{/if}
{/if}

<style>
	* {
		box-sizing: border-box;
	}
	.anchor-wrapper {
		z-index: 10;
		width: fit-content;
		height: fit-content;
		pointer-events: all;
	}

	.locked {
		cursor: not-allowed !important;
	}
	div {
		background: none;
		border: none;
		padding: 0;
		font: inherit;
		cursor: pointer;
		outline: inherit;
	}
</style>
