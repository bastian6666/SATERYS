<script context="module">import SelectionBox from "../../components/SelectionBox/SelectionBox.svelte";
import Background from "../Background/Background.svelte";
import GraphRenderer from "../../renderers/GraphRenderer/GraphRenderer.svelte";
import Editor from "../../components/Editor/Editor.svelte";
import { connectingFrom } from "../../components/Anchor/Anchor.svelte";
import { onMount, setContext, createEventDispatcher, tick } from "svelte";
import { isArrow } from "../../types";
import { moveElementWithBounds, calculateRelativeBounds } from "../../utils/movers";
import { touchDistance, initialClickPosition, tracking } from "../../stores/CursorStore";
import { calculateFitView, calculateTranslation, calculateZoom, generateKey } from "../../utils";
import { get, writable, readable } from "svelte/store";
import { getRandomColor } from "../../utils";
import { moveElement, zoomAndTranslate } from "../../utils/movers";
import { getSnappedPosition } from "../../utils/snapGrid";
</script>

<script>export let graph;
export let width;
export let height;
export let minimap = false;
export let controls = false;
export let toggle = false;
export let fixedZoom = false;
export let pannable = true;
export let disableSelection = false;
export let ZOOM_INCREMENT = 0.1;
export let PAN_INCREMENT = 50;
export let PAN_TIME = 250;
export let MAX_SCALE = 3;
export let MIN_SCALE = 0.2;
export let selectionColor;
export let backgroundExists;
export let fitView = false;
export let trackpadPan;
export let modifier;
export let theme = "light";
export let title;
export let drawer = false;
export let contrast = false;
console.log("Initial Graph drawer prop:", drawer);
let animationFrameId;
const dispatch = createEventDispatcher();
const activeIntervals = {};
const duplicate = writable(false);
const mounted = writable(0);
const graphDOMElement = writable(null);
const cursor = graph.cursor;
const scale = graph.transforms.scale;
const dimensionsStore = graph.dimensions;
const translation = graph.transforms.translation;
const groups = graph.groups;
const groupBoxes = graph.groupBoxes;
const selected = $groups.selected.nodes;
const activeGroup = graph.activeGroup;
const initialNodePositions = graph.initialNodePositions;
const editing = graph.editing;
const nodeBounds = graph.bounds.nodeBounds;
let initialDistance = 0;
let initialScale = 1;
let anchor = { x: 0, y: 0, top: 0, left: 0 };
let selecting = false;
let creating = false;
let adding = false;
let isMovable = false;
let pinching = false;
let initialFit = false;
let graphDimensions;
let toggleComponent = null;
let minimapComponent = null;
let controlsComponent = null;
let drawerComponent = null;
let contrastComponent = null;
$:
  dimensions = $dimensionsStore;
$:
  if (theme)
    document.documentElement.setAttribute("svelvet-theme", theme);
$:
  if (!initialFit && fitView) {
    fitIntoView();
  }
$:
  if (toggle && !toggleComponent)
    loadToggle();
$:
  if (minimap && !minimapComponent)
    loadMinimap();
$:
  if (controls && !controlsComponent)
    loadControls();
$:
  if (drawer && !drawerComponent)
    loadDrawer();
$:
  if (contrast && !contrastComponent)
    loadContrast();
$:
  console.log("Reactive Graph drawer prop:", drawer);
const cursorAnchor = {
  id: null,
  position: graph.cursor,
  offset: writable({ x: 0, y: 0 }),
  connected: writable(/* @__PURE__ */ new Set()),
  dynamic: writable(false),
  edge: null,
  edgeColor: writable(null),
  direction: writable("self"),
  inputKey: null,
  type: "output",
  moving: readable(false),
  store: null,
  mounted: writable(true),
  rotation: readable(0),
  node: {
    zIndex: writable(Infinity),
    rotating: writable(false),
    position: graph.cursor,
    dimensions: { width: writable(0), height: writable(0) }
  }
};
setContext("graphDOMElement", graphDOMElement);
setContext("cursorAnchor", cursorAnchor);
setContext("duplicate", duplicate);
setContext("graph", graph);
setContext("transforms", graph.transforms);
setContext("dimensions", graph.dimensions);
setContext("locked", graph.locked);
setContext("groups", graph.groups);
setContext("bounds", graph.bounds);
setContext("edgeStore", graph.edges);
setContext("nodeStore", graph.nodes);
setContext("mounted", mounted);
onMount(() => {
  console.log("Graph component mounted with drawer1:", drawer);
  updateGraphDimensions();
});
async function fitIntoView() {
  await tick();
  tracking.set(true);
  const { x, y, scale: scale2 } = calculateFitView(graphDimensions, $nodeBounds);
  if (x !== null && y !== null && scale2 !== null) {
    graph.transforms.scale.set(scale2);
    translation.set({ x, y });
  }
  tracking.set(false);
  initialFit = true;
}
async function loadMinimap() {
  minimapComponent = (await import("../../components/Minimap/Minimap.svelte")).default;
}
async function loadToggle() {
  toggleComponent = (await import("../../components/ThemeToggle/ThemeToggle.svelte")).default;
}
async function loadControls() {
  controlsComponent = (await import("../../components/Controls/Controls.svelte")).default;
}
async function loadDrawer() {
  drawerComponent = (await import("../../components/Drawer/DrawerController.svelte")).default;
}
async function loadContrast() {
  contrastComponent = (await import("../../components/ContrastTheme/ContrastTheme.svelte")).default;
}
function updateGraphDimensions() {
  if (!$graphDOMElement)
    return;
  const DOMRect = $graphDOMElement.getBoundingClientRect();
  graphDimensions = {
    top: DOMRect.top,
    left: DOMRect.left,
    bottom: DOMRect.bottom,
    right: DOMRect.right,
    width: DOMRect.width,
    height: DOMRect.height
  };
  graph.dimensions.set(graphDimensions);
  if (fitView === "resize")
    fitIntoView();
}
function onMouseUp(e) {
  if (creating) {
    const groupName = generateKey();
    const groupKey = `${groupName}/${graph.id}`;
    const cursorPosition = get(cursor);
    const width2 = cursorPosition.x - $initialClickPosition.x;
    const height2 = cursorPosition.y - $initialClickPosition.y;
    const top = Math.min($initialClickPosition.y, $initialClickPosition.y + height2);
    const left = Math.min($initialClickPosition.x, $initialClickPosition.x + width2);
    const dimensions2 = {
      width: writable(Math.abs(width2)),
      height: writable(Math.abs(height2))
    };
    const position = writable({
      x: left,
      y: top
    });
    const groupBox = {
      group: writable(groupKey),
      dimensions: dimensions2,
      position,
      color: writable(getRandomColor()),
      moving: writable(false)
    };
    groupBoxes.add(groupBox, groupKey);
    Array.from($selected).forEach((node) => {
      node.group.set(groupKey);
    });
    groups.update((groups2) => {
      const newGroup = {
        parent: writable(groupBox),
        nodes: writable(/* @__PURE__ */ new Set([...$selected, groupBox]))
      };
      groups2[groupKey] = newGroup;
      return groups2;
    });
    $selected = /* @__PURE__ */ new Set();
    creating = false;
    selecting = false;
  }
  if ($activeGroup) {
    const nodeGroupArray = Array.from(get($groups[$activeGroup].nodes));
    nodeGroupArray.forEach((node) => {
      const snappedPos = getSnappedPosition(get(node.position).x, get(node.position).y);
      node.position.set(snappedPos);
      node.moving.set(false);
    });
  }
  const cursorEdge = graph.edges.get("cursor");
  if (cursorEdge) {
    graph.edges.delete("cursor");
    if (!cursorEdge.disconnect) {
      dispatch("edgeDrop", {
        cursor: get(cursor),
        source: {
          node: $connectingFrom?.anchor.node.id.slice(2),
          anchor: $connectingFrom?.anchor.id.split("/")[0].slice(2)
        }
      });
    }
  }
  $activeGroup = null;
  $initialClickPosition = { x: 0, y: 0 };
  $initialNodePositions = [];
  selecting = false;
  isMovable = false;
  $tracking = false;
  if (!e.shiftKey) {
    connectingFrom.set(null);
  }
  anchor.y = 0;
  anchor.x = 0;
}
function onMouseDown(e) {
  if (!pannable && !(e.shiftKey || e.metaKey))
    return;
  if (e.button === 2)
    return;
  if ($graphDOMElement)
    $graphDOMElement.focus();
  const { clientX, clientY } = e;
  $initialClickPosition = get(cursor);
  if (e.shiftKey || e.metaKey) {
    e.preventDefault();
    selecting = true;
    const { top, left } = dimensions;
    anchor.y = clientY - top;
    anchor.x = clientX - left;
    anchor.top = top;
    anchor.left = left;
    if (e.shiftKey && e.metaKey) {
      creating = true;
    } else {
      creating = false;
    }
    if (e.metaKey && !e.shiftKey) {
      adding = true;
    } else {
      adding = false;
    }
  } else {
    isMovable = true;
    $selected = /* @__PURE__ */ new Set();
    $selected = $selected;
  }
}
function onTouchStart(e) {
  $selected = /* @__PURE__ */ new Set();
  $selected = $selected;
  $initialClickPosition = get(cursor);
  isMovable = true;
  if (e.touches.length === 2) {
    startPinching();
    initialDistance = $touchDistance;
    initialScale = $scale;
  }
}
function onTouchEnd() {
  isMovable = false;
  pinching = false;
}
function startPinching() {
  if (!pinching) {
    pinching = true;
    animationFrameId = requestAnimationFrame(handlePinch);
  }
}
function handlePinch() {
  if (!pinching) {
    cancelAnimationFrame(animationFrameId);
    return;
  }
  const newDistance = $touchDistance;
  const scaleFactor = newDistance / initialDistance;
  $scale = initialScale * scaleFactor;
  animationFrameId = requestAnimationFrame(handlePinch);
}
function handleKeyDown(e) {
  const { key, code } = e;
  const target = e.target;
  if (target.tagName == "INPUT" || target.tagName == "TEXTAREA")
    return;
  if (code === "KeyA" && e[`${modifier}Key`]) {
    const unlockedNodes = graph.nodes.getAll().filter((node) => !get(node.locked));
    $selected = new Set(unlockedNodes);
  } else if (isArrow(key)) {
    handleArrowKey(key, e);
  } else if (key === "=") {
    zoomAndTranslate(-1, graph.dimensions, graph.transforms, ZOOM_INCREMENT);
  } else if (key === "-") {
    zoomAndTranslate(1, graph.dimensions, graph.transforms, ZOOM_INCREMENT);
  } else if (key === "0") {
    fitIntoView();
  } else if (key === "Control") {
    $groups["selected"].nodes.set(/* @__PURE__ */ new Set());
  } else if (code === "KeyD" && e[`${modifier}Key`]) {
    duplicate.set(true);
    setTimeout(() => {
      duplicate.set(false);
    }, 100);
  } else if (key === "Tab" && (e.altKey || e.ctrlKey)) {
    selectNextNode();
  } else if (key === "l") {
    theme = theme === "light" ? "dark" : "light";
  } else if (key === "d") {
    drawer = !drawer;
  } else if (key === "m") {
    minimap = !minimap;
  } else if (key === "c") {
    controls = !controls;
  } else if (key === "e") {
    const node = Array.from($selected)[0];
    graph.editing.set(node);
  } else {
    return;
  }
  e.preventDefault();
}
function handleDrop(e) {
  e.preventDefault();
  const graphRect = $graphDOMElement?.getBoundingClientRect();
  if (!graphRect)
    return;
  const mouseX = e.clientX - graphRect.left;
  const mouseY = e.clientY - graphRect.top;
  const { x: snappedX, y: snappedY } = getSnappedPosition(mouseX, mouseY);
  console.log(`Dropped Node at Snapped Position: (${snappedX}, ${snappedY})`);
  if (!draggedNodeType)
    return;
  const newNode = {
    id: `node-${Date.now()}`,
    // Unique ID based on timestamp
    rotation: writable(0),
    // Rotation angle
    position: writable({ x: snappedX, y: snappedY }),
    // Position as a writable store
    moving: writable(false),
    // Initial moving state
    label: writable("New Node"),
    // Default label
    dimensions: {
      width: writable(200),
      // Default width as a writable store
      height: writable(100)
      // Default height as a writable store
    },
    inputs: writable(2),
    // Default number of input anchors
    outputs: writable(2),
    // Default number of output anchors
    anchors: writable([]),
    // Empty anchors array (you may want to define this more specifically)
    group: writable(null),
    // Initially no group
    collapsed: writable(false),
    // Default collapsed state
    resizingWidth: writable(false),
    // Default resizing width state
    resizingHeight: writable(false),
    // Default resizing height state
    rotating: writable(false),
    // Default rotating state
    editable: writable(true),
    // Node is editable by default
    locked: writable(false),
    // Node is not locked by default
    recalculateAnchors: (direction) => {
    },
    // Function for recalculating anchors
    resizable: writable(true),
    // Node is resizable by default
    zIndex: writable(1),
    // Default zIndex
    edge: null,
    // Default edge value (you can specify the type here)
    direction: writable("TD"),
    // Default direction (Top to Down)
    borderRadius: writable(5),
    // Default border radius
    borderWidth: writable(1),
    // Default border width
    connections: writable([]),
    // Empty connections array
    bgColor: writable("#007bff"),
    // Default background color
    borderColor: writable("#000"),
    // Default border color
    selectionColor: writable("#ff0000"),
    // Default selection color
    textColor: writable("#fff")
    // Default text color
  };
  let draggedNodeType = null;
  graph.nodes.add(newNode, newNode.id);
  draggedNodeType = null;
}
function selectNextNode() {
  const nodes = graph.nodes.getAll();
  const currentIndex = nodes.findIndex((node) => $selected.has(node));
  const nextIndex = currentIndex + 1;
  $selected.delete(nodes[currentIndex]);
  $selected.add(nodes[nextIndex]);
}
function handleKeyUp(e) {
  const { key } = e;
  if (isArrow(key)) {
    clearInterval(activeIntervals[key]);
    delete activeIntervals[key];
  } else if (key === "Shift") {
    connectingFrom.set(null);
  }
}
function handleScroll(e) {
  if (fixedZoom)
    return;
  const multiplier = e.shiftKey ? 0.15 : 1;
  const { clientX, clientY, deltaY } = e;
  const currentTranslation = $translation;
  const pointerPosition = { x: clientX, y: clientY };
  if ((trackpadPan || e.metaKey) && deltaY % 1 === 0) {
    $translation = {
      x: $translation.x -= e.deltaX,
      y: $translation.y -= e.deltaY
    };
    return;
  }
  if ($scale >= MAX_SCALE && deltaY < 0 || $scale <= MIN_SCALE && deltaY > 0)
    return;
  const scrollAdjustment = Math.min(9e-3 * multiplier * Math.abs(deltaY), 0.08);
  const newScale = calculateZoom($scale, Math.sign(deltaY), scrollAdjustment);
  const newTranslation = calculateTranslation(
    $scale,
    newScale,
    currentTranslation,
    pointerPosition,
    graphDimensions
  );
  scale.set(newScale);
  translation.set(newTranslation);
}
function handleDragOver(e) {
  e.preventDefault();
}
function handleArrowKey(key, e) {
  const multiplier = e.shiftKey ? 2 : 1;
  const direction = key === "ArrowLeft" || key === "ArrowUp" ? 1 : -1;
  const leftRight = key === "ArrowLeft" || key === "ArrowRight";
  const startOffset = leftRight ? $translation.x : $translation.y;
  const endOffset = startOffset + direction * PAN_INCREMENT * multiplier;
  if (!activeIntervals[key]) {
    const start = performance.now();
    let interval = setInterval(() => {
      const time = performance.now() - start;
      if ($selected.size === 0) {
        const movement = startOffset + (endOffset - startOffset) * (time / PAN_TIME);
        translation.set({
          x: leftRight ? movement : $translation.x,
          y: leftRight ? $translation.y : movement
        });
      } else {
        const delta = {
          x: leftRight ? -direction * 2 : 0,
          y: leftRight ? 0 : -direction * 2
        };
        Array.from($selected).forEach((node) => {
          const currentPosition = get(node.position);
          let groupBox;
          const groupName = get(node.group);
          const groupBoxes2 = get(graph.groupBoxes);
          if (groupName)
            groupBox = groupBoxes2.get(groupName);
          if (groupBox) {
            const nodeWidth = get(node.dimensions.width);
            const nodeHeight = get(node.dimensions.height);
            const bounds = calculateRelativeBounds(groupBox, nodeWidth, nodeHeight);
            moveElementWithBounds(currentPosition, delta, node.position, bounds);
          } else {
            const newPos = {
              x: currentPosition.x + delta.x,
              y: currentPosition.y + delta.y
            };
            const snappedPos = getSnappedPosition(newPos.x, newPos.y);
            node.position.set(snappedPos);
          }
        });
      }
    }, 2);
    activeIntervals[key] = interval;
  }
}
</script>

<!-- <button on:click={() => getJSONState(graph)}>SAVE STATE</button> -->
<!-- svelte-ignore a11y-no-noninteractive-tabindex -->

<section
	role="presentation"
	id={graph.id}
	class="svelvet-wrapper"
	{title}
	style:width={width ? width + 'px' : '100%'}
	style:height={height ? height + 'px' : '100%'}
	style:cursor={pannable ? 'move' : 'default'}
	on:wheel|preventDefault={handleScroll}
	on:mousedown|preventDefault|self={onMouseDown}
	on:touchend|preventDefault={onTouchEnd}
	on:touchstart|preventDefault|self={onTouchStart}
	on:keydown={handleKeyDown}
	on:keyup={handleKeyUp}
	on:dragover|preventDefault={handleDragOver}
	on:drop={handleDrop}
	bind:this={$graphDOMElement}
	tabindex={0}
>
	<GraphRenderer {isMovable}>
		{#if $editing}
			<Editor editing={$editing} />
		{/if}
		<slot />
	</GraphRenderer>

	{#if backgroundExists}
		<slot name="background" />
	{:else}
		<Background />
	{/if}
	{#if minimap}
		<svelte:component this={minimapComponent} />
	{/if}
	{#if controls}
		<svelte:component this={controlsComponent} />
	{/if}
	{#if toggle}
		<svelte:component this={toggleComponent} />
	{/if}
	{#if drawer}
		<svelte:component this={drawerComponent} />
	{/if}
	{#if contrast}
		<svelte:component this={contrastComponent} />
	{/if}
	<slot name="minimap" />
	<slot name="drawer" />
	<slot name="controls" />
	<slot name="toggle" />
	<slot name="contrast" />
	{#if selecting && !disableSelection}
		<SelectionBox {creating} {anchor} {graph} {adding} color={selectionColor} />
	{/if}
</section>

<svelte:window
	on:touchend={onMouseUp}
	on:mouseup={onMouseUp}
	on:resize={updateGraphDimensions}
	on:scroll={updateGraphDimensions}
/>

<style>
	.svelvet-wrapper {
		position: relative;
		overflow: hidden;
		cursor: move;
		font-family: 'Rubik';
		box-sizing: border-box !important;
		user-select: none;
		margin: 0;
		line-height: 1rem;
		font-size: 0.85rem;
		pointer-events: auto;
		color: var(--default-text-color);
	}
	.svelvet-wrapper:focus {
		outline: none;
		box-shadow: 0 0 0 2px rgb(59, 102, 232);
	}
</style>
