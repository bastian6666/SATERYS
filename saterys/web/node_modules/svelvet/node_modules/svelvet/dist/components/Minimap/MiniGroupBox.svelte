<script>export let dimensions;
export let position;
export let color;
export let groupName;
export let top;
export let left;
const { width, height } = dimensions;
</script>

<div
	class="mini-bounding-box"
	id={`mini-${groupName}-bounding-box`}
	style:top={`${$position.y - top}px`}
	style:left={`${$position.x - left}px`}
	style:width={`${$width}px`}
	style:height={`${$height}px`}
	style="border: solid 4px {$color};"
	style:background-color={$color}
/>

<style>
	.mini-bounding-box {
		position: absolute;
		opacity: 25%;
		z-index: -4;
		pointer-events: none;
		border-radius: 10px;
	}
</style>
