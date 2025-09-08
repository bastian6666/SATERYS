<script>import { getContext } from "svelte";
import { isArrow } from "../../../types";
import { roundNum, calculateRelativeCursor } from "../../../utils";
import { tracking } from "../../../stores/CursorStore";
export let minDegree = 60;
export let maxDegree = 300;
export let parameterStore;
export let min = 0;
export let max = 100;
export let step = 1;
export let label = "Value";
export let fixed = 0;
export let fontColor = null;
export let knobColor = "lightblue";
export let knobValueColor = "white";
export let indicatorColor = "#666565";
$parameterStore = $parameterStore < min ? min : $parameterStore > max ? max : Math.floor(($parameterStore - min) / step) * step + min;
$:
  currentDegree = ($parameterStore - min) / (max - min) * (maxDegree - minDegree) + minDegree;
$:
  connected = typeof parameterStore.set !== "function";
const graph = getContext("graph");
const groups = graph.groups;
const selected = $groups.selected;
const activeGroup = graph.activeGroup;
let sliderWidth;
let knobWrapperElement;
let knobElement;
let rotating = false;
$:
  cursor = graph.cursor;
$:
  scale = graph.transforms.scale;
$:
  translation = graph.transforms.translation;
$:
  if (rotating) {
    calculateNewAngle($cursor.x, $cursor.y);
  }
function startRotate(e) {
  e.stopPropagation();
  e.preventDefault();
  window.addEventListener("mouseup", stopRotate, { once: true });
  rotating = true;
}
let previousValue = $parameterStore;
function startTouchRotate(e) {
  $activeGroup = null;
  selected.nodes.set(/* @__PURE__ */ new Set());
  tracking.set(false);
  e.stopPropagation();
  e.preventDefault();
  window.addEventListener("touchend", stopRotate, { once: true });
  rotating = true;
}
function stopRotate() {
  if (previousValue === $parameterStore) {
    knobElement.focus();
  } else {
    previousValue = $parameterStore;
  }
  rotating = false;
  window.removeEventListener("mouseup", stopRotate);
}
function rotatable(node) {
  node.addEventListener("mousedown", startRotate);
  node.addEventListener("touchstart", startTouchRotate);
  return {
    destroy() {
      node.removeEventListener("mousedown", startRotate);
    }
  };
}
function updateValue(delta, increment = (maxDegree - minDegree) / (max - min) * step) {
  currentDegree = roundNum(
    Math.max(minDegree, Math.min(currentDegree + delta * increment, maxDegree)),
    3
  );
  $parameterStore = (clamp(currentDegree) - minDegree) / (maxDegree - minDegree) * (max - min) + min;
}
$:
  curAngle = `rotate(${currentDegree}deg`;
export function clamp(num) {
  const increment = (maxDegree - minDegree) / (max - min) * step;
  const degreeRoundToStep = Math.round((num - minDegree) / increment) * increment + minDegree;
  const degree = Math.min(Math.max(degreeRoundToStep, minDegree), maxDegree);
  currentDegree = degree;
  return degree;
}
function calculateNewAngle(cursorX, cursorY) {
  const { top, left, width, height } = knobWrapperElement.getBoundingClientRect();
  const e = { clientX: cursorX, clientY: cursorY };
  const { x, y } = calculateRelativeCursor(e, top, left, width, height, $scale, $translation);
  const relativeX = x + 2 * $translation.x / $scale - width / 2;
  const relativeY = height / 2 - (y + 2 * $translation.y / $scale);
  let angle = relativeX > 0 && relativeY > 0 ? 270 - Math.atan(relativeY / relativeX) * (180 / Math.PI) : relativeX < 0 && relativeY > 0 ? Math.atan(relativeY / -relativeX) * (180 / Math.PI) + 90 : relativeX > 0 && relativeY < 0 ? 270 + Math.atan(-relativeY / relativeX) * (180 / Math.PI) : relativeX < 0 && relativeY < 0 ? 90 - Math.atan(-relativeY / -relativeX) * (180 / Math.PI) : currentDegree;
  $parameterStore = Number(
    ((clamp(angle) - minDegree) / (maxDegree - minDegree) * (max - min) + min).toFixed(fixed)
  );
}
</script>

{#if !connected}
	<!-- this div is wrapping the knob section -->
	<div class="wrapper" style:color={fontColor} bind:this={knobWrapperElement}>
		<div class="knob-container" bind:offsetWidth={sliderWidth} style:transform={curAngle}>
			<div
				tabindex={0}
				id="knob"
				class="knob"
				aria-label="knob component"
				role="slider"
				aria-valuemin={min}
				aria-valuemax={max}
				aria-valuenow={$parameterStore}
				style:background={knobColor}
				on:wheel|stopPropagation|preventDefault={(event) => {
					updateValue(Math.sign(event.deltaY));
				}}
				on:keydown|stopPropagation={(e) => {
					const { key } = e;

					if (isArrow(key)) {
						e.preventDefault();
						updateValue(key == 'ArrowDown' ? -1 : key == 'ArrowUp' ? 1 : 0);
					}
				}}
				use:rotatable
				bind:this={knobElement}
			/>
			<div class="indicator" style:background={indicatorColor} />
		</div>
		<div class="knob-value" style:color={knobValueColor}>
			{$parameterStore.toFixed(fixed)}
		</div>
	</div>
{:else}
	<div class="wrapper connected">
		<div class="knob connected" style:--percentage="10%" aria-label={label}>
			<p>{label}</p>
			<p>{currentDegree}</p>
		</div>
	</div>
{/if}

<style>
	* {
		box-sizing: border-box;
	}

	.wrapper {
		display: flex;
		gap: 0.5rem;
		justify-content: center;
		align-items: center;
		height: 7rem;
		width: 7rem;
	}

	.knob {
		display: flex;
		border-radius: 50%;
		width: 7rem;
		height: 7rem;
		pointer-events: auto;
		cursor: pointer;
		padding: 0.25rem;
	}

	.indicator {
		top: 80%;
		left: 48%;
		transform-origin: 50% -50%;
		position: absolute;
		width: 4%;
		height: 15%;
		background-color: #666565;
		border-radius: 30%/10%;
		pointer-events: none;
	}
	.knob-value {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, 50%);
		font-size: 2.5em;
		color: white;
		z-index: 100;
	}

	.connected {
		display: flex;
		justify-content: space-between;
		padding: 0.25rem 0.5rem;
	}
</style>
