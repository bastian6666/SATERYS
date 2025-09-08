<script>import { getContext } from "svelte";
import { initialClickPosition } from "../../stores/CursorStore";
import { updateTranslation } from "../../utils";
import { get } from "svelte/store";
const graph = getContext("graph");
const transforms = graph.transforms;
const scale = transforms.scale;
const translation = transforms.translation;
const cursor = graph.cursor;
export let isMovable;
let animationFrameId;
let moving = false;
$:
  graphTranslation = $translation;
$:
  transform = `translate(${graphTranslation.x}px, ${graphTranslation.y}px) scale(${$scale})`;
$:
  if (isMovable && !moving) {
    moving = true;
    animationFrameId = requestAnimationFrame(translate);
  } else if (!isMovable || !moving) {
    moving = false;
    cancelAnimationFrame(animationFrameId);
  }
function translate() {
  $translation = updateTranslation(get(initialClickPosition), $cursor, transforms);
  animationFrameId = requestAnimationFrame(translate);
}
</script>

<div
	on:contextmenu|preventDefault|self
	on:click|preventDefault|self
	on:touchstart|preventDefault|self
	style:transform
	class="svelvet-graph-wrapper"
	role="presentation"
>
	<slot />
</div>

<style>
	.svelvet-graph-wrapper {
		box-sizing: border-box;
		position: absolute;
		width: 100%;
		height: 100%;
		pointer-events: none !important;
		touch-action: none;
		/* outline: solid 1px red; */
	}
</style>
