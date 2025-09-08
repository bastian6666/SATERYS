<script context="module">import arrow_left from "./arrow_left.svelte";
import arrow_right from "./arrow_right.svelte";
import dark_mode from "./dark_mode.svelte";
import light_mode from "./light_mode.svelte";
import filter_center_focus from "./filter_center_focus.svelte";
import lock from "./lock.svelte";
import lock_open from "./lock_open.svelte";
import north_west from "./north_west.svelte";
import south_east from "./south_east.svelte";
import zoom_in from "./zoom_in.svelte";
import zoom_out from "./zoom_out.svelte";
import visibility_off from "./visibility_off.svelte";
</script>

<script>export let width = 16;
export let icon;
const icons = {
  arrow_left,
  arrow_right,
  dark_mode,
  light_mode,
  filter_center_focus,
  lock,
  lock_open,
  north_west,
  south_east,
  zoom_in,
  zoom_out,
  visibility_off
};
</script>

<svg xmlns="http://www.w3.org/2000/svg" height={width} viewBox="0 -960 960 960" {width}>
	<svelte:component this={icons[icon]} />
</svg>

<style>
	svg {
		fill: currentColor;
	}
</style>
