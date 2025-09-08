<script>import { setContext } from "svelte";
export let edge;
setContext("edge", edge);
</script>

<slot />
