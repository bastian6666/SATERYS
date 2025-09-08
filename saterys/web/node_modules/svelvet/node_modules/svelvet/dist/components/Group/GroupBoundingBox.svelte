<script>import { createEventDispatcher } from "svelte";
export let dimensions;
export let position;
export let color;
export let groupName;
const { width, height } = dimensions;
$:
  id = `${groupName}-bounding-box`;
const dispatch = createEventDispatcher();
function dispatchClick() {
  dispatch("groupClick", { groupName });
}
</script>

<div
	role="button"
	tabindex="0"
	on:contextmenu|stopPropagation|preventDefault
	on:mousedown|stopPropagation|preventDefault={dispatchClick}
	class="bounding-box-border"
	{id}
	style:top={`${$position.y}px`}
	style:left={`${$position.x}px`}
	style:width={`${$width}px`}
	style:height={`${$height}px`}
	style="border: solid 4px {$color};"
>
	<div class="bounding-box" style:background-color={$color} />
</div>

<style>
	.bounding-box {
		width: 100%;
		height: 100%;
		opacity: 25%;
		z-index: -4;
		pointer-events: none;
	}
	.bounding-box-border {
		position: absolute;
		overflow: hidden;
		border-radius: 10px;
		pointer-events: auto;
		z-index: -4;
	}
</style>
