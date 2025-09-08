<script>import GroupBoundingBox from "../../components/Group/GroupBoundingBox.svelte";
import { getContext } from "svelte";
const graph = getContext("graph");
const groupBoxes = graph.groupBoxes;
</script>

{#each Array.from($groupBoxes) as [id, group] (id)}
	<GroupBoundingBox on:groupClick {...group} groupName={id} />
{/each}
