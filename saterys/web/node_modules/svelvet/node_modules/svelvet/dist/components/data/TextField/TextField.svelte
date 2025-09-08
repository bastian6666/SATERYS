<script>import { getContext } from "svelte";
export let placeholder;
const textStore = getContext("textStore");
</script>

<input
	on:keydown|stopPropagation
	on:click|stopPropagation
	on:mousedown|stopPropagation
	{placeholder}
	type="text"
	bind:value={$textStore}
/>
