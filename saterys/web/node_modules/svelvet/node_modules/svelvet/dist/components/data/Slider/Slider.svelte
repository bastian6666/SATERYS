<script>import { initialClickPosition } from "../../../stores/CursorStore";
import { getContext } from "svelte";
import { isArrow } from "../../../types";
import { roundNum } from "../../../utils";
import { tracking } from "../../../stores/CursorStore";
export let parameterStore;
export let min = 0;
export let max = 100;
export let step = 1;
export let label = "Value";
export let fixed = 2;
export let fontColor = null;
export let barColor = null;
export let bgColor = null;
$:
  connected = typeof parameterStore.set !== "function";
let graph = getContext("graph");
let node = getContext("node");
const groups = graph.groups;
const selected = $groups.selected;
const activeGroup = graph.activeGroup;
$:
  width = node.dimensions.width;
let sliderWidth;
let sliderElement;
let sliding = false;
let previousX = 0;
let pixelsMoved = 0;
$:
  cursor = graph.cursor;
$:
  if (sliding) {
    const deltaX = $cursor.x - previousX;
    calculateSlide(deltaX);
    previousX = $cursor.x;
  }
function startSlide(e) {
  e.stopPropagation();
  e.preventDefault();
  $initialClickPosition = { x: $cursor.x, y: $cursor.y };
  previousX = $cursor.x;
  window.addEventListener("mouseup", stopSlide, { once: true });
  sliding = true;
}
let previousValue = $parameterStore;
function startTouchSlide(e) {
  $activeGroup = null;
  selected.nodes.set(/* @__PURE__ */ new Set());
  tracking.set(false);
  e.stopPropagation();
  e.preventDefault();
  $initialClickPosition = { x: $cursor.x, y: $cursor.y };
  previousX = $cursor.x;
  window.addEventListener("touchend", stopSlide, { once: true });
  sliding = true;
}
function stopSlide() {
  if (previousValue === $parameterStore) {
    sliderElement.focus();
    sliderElement.select();
  } else {
    previousValue = $parameterStore;
  }
  sliding = false;
  window.removeEventListener("mouseup", stopSlide);
}
function slideable(node2) {
  node2.addEventListener("mousedown", startSlide);
  node2.addEventListener("touchstart", startTouchSlide);
  return {
    destroy() {
      node2.removeEventListener("mousedown", startSlide);
    }
  };
}
function updateValue(delta, increment = step) {
  if (typeof $parameterStore !== "number")
    return;
  $parameterStore = roundNum(
    Math.max(min, Math.min($parameterStore + delta * increment, max)),
    3
  );
}
function calculateSlide(cursorChange, increment = step) {
  if (typeof $parameterStore !== "number")
    return;
  const pixelsToMove = $width * 0.7 / ((max - min) / increment);
  pixelsMoved += cursorChange;
  if (Math.abs(pixelsMoved) >= pixelsToMove) {
    const incrementsToMove = Math.floor(Math.abs(pixelsMoved) / pixelsToMove);
    if (pixelsMoved > 0) {
      updateValue(incrementsToMove);
    } else {
      updateValue(-incrementsToMove);
    }
    pixelsMoved = pixelsMoved > 0 ? pixelsMoved - incrementsToMove * pixelsToMove : pixelsMoved + incrementsToMove * pixelsToMove;
  }
}
function validateInput() {
  const number = parseFloat(sliderElement.value);
  if (!Number.isNaN(number)) {
    if (number <= min) {
      $parameterStore = min;
    } else if (number >= max) {
      $parameterStore = max;
    } else {
      $parameterStore = roundNum(number, 2);
    }
  }
  sliderElement.value = JSON.stringify($parameterStore);
  sliderElement.blur();
}
$:
  percentageSlid = ($parameterStore - min) / (max - min) * 100;
$:
  CSSpercentage = `${percentageSlid}%`;
$:
  sliderStyle = `linear-gradient(
			90deg,
			${barColor || "var(--primary-color, var(--default-primary-color))"} ${CSSpercentage},
			${bgColor || "var(--accent-color, var(--default-accent-color))"} ${CSSpercentage}
		)`;
</script>

{#if !connected}
	<div class="wrapper" style:color={fontColor}>
		<button
			class="button"
			on:touchstart|stopPropagation={() => updateValue(-1)}
			on:mousedown|stopPropagation={() => updateValue(-1)}>−</button
		>
		<div class="slider" bind:offsetWidth={sliderWidth}>
			<label for="slider-input" class="input-label">{label}</label>
			<input
				tabindex={0}
				id="slider-input"
				class="slider-input"
				style:background={sliderStyle}
				style:--percentage={CSSpercentage}
				type="text"
				value={$parameterStore.toFixed(fixed)}
				aria-label={label}
				on:wheel|stopPropagation|preventDefault={(event) => {
					updateValue(Math.sign(event.deltaY), step);
				}}
				on:keydown|stopPropagation={(e) => {
					const { key } = e;

					if (isArrow(key)) {
						e.preventDefault(); // Stops cursor from moving
						updateValue(key == 'ArrowDown' ? -1 : key == 'ArrowUp' ? 1 : 0);
					}

					if (key === 'Enter') validateInput();
				}}
				use:slideable
				bind:this={sliderElement}
			/>
		</div>
		<button
			class="button"
			on:touchstart|stopPropagation={() => updateValue(1)}
			on:mousedown|stopPropagation={() => updateValue(1)}>+</button
		>
	</div>
{:else}
	<div class="wrapper connected">
		<div class="slider-input connected" style:--percentage="100%" aria-label={label}>
			<p>{label}</p>
			<p>{$parameterStore}</p>
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
	}

	.slider-input {
		border: none;
		border-radius: 6px;
		color: inherit;
		text-align: right;
		width: 100%;
		height: 1.5rem;
		cursor: ew-resize;
		padding: 0.25rem;
		pointer-events: auto;
	}

	.button {
		background: none;
		border: none;
		font-size: 1.5rem;
		color: inherit;
		line-height: 1rem;
		cursor: pointer;
		display: flex;
		align-items: baseline;
		justify-content: center;
	}
	.button:hover {
		opacity: 50%;
	}

	.slider {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100%;
		pointer-events: auto;
	}

	.connected {
		display: flex;
		justify-content: space-between;
		padding: 0.25rem 0.5rem;
	}
	.input-label {
		margin-left: 0.5rem;
		position: absolute;
		pointer-events: none;
		color: inherit;
	}
</style>
