<script context="module">import { initialClickPosition, tracking } from "../../stores";
import { captureGroup } from "../../utils";
import { getContext, onDestroy, onMount, setContext } from "svelte";
import { createEventDispatcher } from "svelte";
import { get, writable } from "svelte/store";
const tagsToIgnore = /* @__PURE__ */ new Set(["INPUT", "SELECT", "BUTTON", "TEXTAREA"]);
</script>

<script>const mounted = getContext("mounted");
const duplicate = getContext("duplicate");
const graphDOMElement = getContext("graphDOMElement");
const dispatch = createEventDispatcher();
export let node;
export let isDefault;
export let useDefaults;
export let center;
export let nodeStore;
export let locked;
export let groups;
export let maxZIndex;
export let centerPoint;
export let cursor;
export let initialNodePositions;
export let activeGroup;
export let editing;
export let dimensionsProvided = false;
export let title;
const anchorsMounted = writable(0);
const nodeConnectEvent = writable(null);
const id = node.id;
const position = node.position;
const widthStore = node.dimensions.width;
const heightStore = node.dimensions.height;
const selectionColor = node.selectionColor;
const editable = node.editable;
const nodeLock = node.locked;
const zIndex = node.zIndex;
const bgColor = node.bgColor;
const borderRadius = node.borderRadius;
const textColor = node.textColor;
const group = node.group;
const borderColor = node.borderColor;
const borderWidth = node.borderWidth;
const rotation = node.rotation;
const { selected: selectedNodeGroup, hidden: hiddenNodesGroup } = $groups;
const hiddenNodes = hiddenNodesGroup.nodes;
const selectedNodes = selectedNodeGroup.nodes;
const resized = writable(false);
$:
  actualPosition = $position;
$:
  selected = $selectedNodes.has(node);
$:
  hidden = $hiddenNodes.has(node);
$:
  fixedSizing = dimensionsProvided || $resized;
$:
  if (selected && $duplicate) {
    dispatch("duplicate", node);
  }
setContext("node", node);
setContext("anchorsMounted", anchorsMounted);
setContext("resized", resized);
setContext("nodeConnectEvent", nodeConnectEvent);
onMount(() => {
  if (center) {
    const opticalCenter = {
      x: $centerPoint.x - $widthStore / 2,
      y: $centerPoint.y - $heightStore / 2
    };
    node.position.set(opticalCenter);
    tracking.set(true);
    tracking.set(false);
  }
  mounted.update((n) => n + 1);
});
onDestroy(() => {
  if (selected) {
    $selectedNodes.delete(node);
    $selectedNodes = $selectedNodes;
  }
  mounted.update((n) => n - 1);
});
function toggleSelected() {
  if (selected) {
    if (node)
      $selectedNodes.delete(node);
    $selectedNodes = $selectedNodes;
  } else {
    if (node)
      $selectedNodes.add(node);
    $selectedNodes = $selectedNodes;
  }
}
function handleNodeClicked(e) {
  $initialClickPosition = get(cursor);
  $graphDOMElement.focus();
  if ($zIndex !== $maxZIndex && $zIndex !== Infinity)
    $zIndex = ++$maxZIndex;
  const targetElement = e.target;
  if (tagsToIgnore.has(targetElement.tagName))
    return;
  e.preventDefault();
  dispatch("nodeClicked", { node, e });
  if ($locked || $nodeLock)
    return;
  if ("touches" in e) {
    if (e.touches && e.touches.length > 1)
      return;
  } else {
    if (e.button === 2 && $editable) {
      $editing = node;
    }
  }
  $tracking = true;
  nodeSelectLogic(e);
}
function nodeSelectLogic(e) {
  let groupData;
  let parent;
  let isParent = false;
  const nodeGroup = $group;
  if (nodeGroup) {
    groupData = $groups[nodeGroup];
    parent = get(groupData.parent);
    isParent = parent === node;
  }
  if (isParent) {
    $activeGroup = nodeGroup;
  } else {
    $activeGroup = "selected";
  }
  if (!e.shiftKey && selected) {
    $activeGroup = "selected";
  } else {
    if (!e.shiftKey && !selected && !e.shiftKey) {
      $selectedNodes.clear();
      $selectedNodes = $selectedNodes;
    }
    toggleSelected();
  }
  $initialNodePositions = captureGroup($groups["selected"].nodes);
}
function destroy() {
  nodeStore.delete(id);
}
function onMouseUp(e) {
  const cursorPosition = get(cursor);
  const mouseDeltaX = cursorPosition.x - $initialClickPosition.x;
  const mouseDeltaY = cursorPosition.y - $initialClickPosition.y;
  const combinedDelta = Math.abs(mouseDeltaX) + Math.abs(mouseDeltaY);
  if (combinedDelta < 4)
    dispatch("nodeReleased", { e, node });
  $nodeConnectEvent = e;
}
function grabHandle(node2) {
  node2.addEventListener("mousedown", handleNodeClicked);
  node2.addEventListener("touchstart", handleNodeClicked);
  return {
    destroy() {
      node2.removeEventListener("mousedown", handleNodeClicked);
      node2.removeEventListener("touchstart", handleNodeClicked);
    }
  };
}
</script>

{#if !hidden}
	<div
		{id}
		class="svelvet-node"
		role="button"
		class:selected
		class:locked={$locked || $nodeLock}
		style:top="{actualPosition.y}px"
		style:left="{actualPosition.x}px"
		style:z-index={$zIndex}
		{title}
		style:width={fixedSizing ? $widthStore + 'px' : 'fit-content'}
		style:height={fixedSizing ? $heightStore + 'px' : 'fit-content'}
		style:transform="rotate({$rotation}deg)"
		style:--prop-background-color={$bgColor || (isDefault || useDefaults ? null : 'transparent')}
		style:--prop-text-color={$textColor}
		style:--prop-border-color={$borderColor}
		style:--prop-selection-color={$selectionColor}
		style:--prop-border-radius={$borderRadius
			? `${$borderRadius}px`
			: isDefault || useDefaults
			? null
			: '0px'}
		style:--prop-border-width={$borderWidth || (isDefault || useDefaults ? null : '0px')}
		on:contextmenu|preventDefault|stopPropagation
		on:mouseup={onMouseUp}
		use:grabHandle
		tabindex={0}
	>
		{#if !fixedSizing}
			<div
				style:width="fit-content"
				style:height="fit-content"
				bind:clientHeight={$heightStore}
				bind:clientWidth={$widthStore}
			>
				<slot {grabHandle} {selected} {destroy} />
			</div>
		{:else}
			<slot {grabHandle} {selected} {destroy} />
		{/if}

		<div id={`anchors-west-${node.id}`} class="anchors left">
			<slot name="anchorWest" />
		</div>
		<div id={`anchors-east-${node.id}`} class="anchors right">
			<slot name="anchorEast" />
		</div>
		<div id={`anchors-north-${node.id}`} class="anchors top">
			<slot name="anchorNorth" />
		</div>
		<div id={`anchors-south-${node.id}`} class="anchors bottom">
			<slot name="anchorSouth" />
		</div>
	</div>
{/if}

<style>
	.svelvet-node {
		position: absolute;
		pointer-events: all;
		display: flex;
		justify-content: center;
		align-items: center;
		will-change: top, left;
		cursor: var(--node-cursor, var(--default-node-cursor));
		--final-border-width: var(
			--prop-border-width,
			var(--node-border-width, var(--default-node-border-width))
		);
		--final-border-color: var(
			--prop-border-color,
			var(--node-border-color, var(--default-node-border-color))
		);
		--final-selection-color: var(
			--prop-selection-color,
			var(--node-selection-color, var(--default-node-selection-color))
		);

		border-radius: var(
			--prop-border-radius,
			var(--node-border-radius, var(--default-node-border-radius))
		);
		background-color: var(--prop-background-color, var(--node-color, var(--default-node-color)));
		color: var(--prop-text-color, var(--text-color, var(--default-text-color)));
		box-shadow: 0 0 0 var(--final-border-width) var(--final-border-color),
			var(--default-node-shadow);
		font-family: 'Roboto', sans-serif;
	}
	.anchors {
		/* outline: solid 1px red; */
		display: flex;
		position: absolute;
		justify-content: center;
		align-items: center;
		z-index: 1;
		pointer-events: none;
	}
	.top,
	.bottom {
		width: 100%;
		justify-content: space-around;
	}

	.top {
		transform: translate(0px, -50%);
		top: 0px;
	}

	.bottom {
		transform: translate(0px, 50%);
		bottom: 0px;
	}

	.left,
	.right {
		height: 100%;
		flex-direction: column;
		justify-content: space-around;
	}

	.left {
		transform: translate(-50%);
		left: 0px;
	}

	.right {
		transform: translate(50%);
		right: 0px;
	}

	.locked {
		cursor: var(--node-cursor-blocked, var(--default-node-cursor-blocked));
	}
	.selected {
		box-shadow: 0 0 0 var(--final-border-width) var(--final-selection-color),
			var(--default-node-shadow);
	}
</style>
