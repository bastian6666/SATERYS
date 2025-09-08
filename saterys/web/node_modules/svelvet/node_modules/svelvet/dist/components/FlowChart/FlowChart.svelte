<script>import Node from "../Node/Node.svelte";
import { onMount, getContext, setContext } from "svelte";
import { flowChartDrawer } from "../../utils/drawers/flowchartDrawer";
import { flowChartParser } from "../../utils/helpers/parser";
export let mermaid = "";
export let mermaidConfig = {};
const flowChart = flowChartParser(mermaid);
setContext("flowchart", flowChart);
const grid = flowChartDrawer(flowChart);
const graph = getContext("graph");
const MIN_X_SPACE = 100;
const MIN_Y_SPACE = 100;
let nodeList;
onMount(() => {
  graph.nodes.subscribe((nodes) => nodeList = Object.fromEntries(nodes));
  let y = 0;
  for (const row of grid) {
    let x = 0;
    let maxHeight = -Infinity;
    for (const node of row) {
      if (!node.ignore) {
        nodeList[`N-${node.id}`].position.update(() => {
          return { x, y };
        });
        nodeList[`N-${node.id}`].dimensions.width.subscribe((width) => x += width);
        nodeList[`N-${node.id}`].dimensions.height.subscribe(
          (height) => maxHeight = Math.max(maxHeight, height)
        );
      }
      x += MIN_X_SPACE;
    }
    y += maxHeight + MIN_Y_SPACE;
  }
});
</script>

{#each grid as row}
	{#each row as node}
		{#if !node.ignore}
			<Node
				label={node.label}
				id={node.id}
				TD={true}
				{...mermaidConfig[node.id]}
				connections={node.children.map((id) => [id, '1'])}
			/>
		{/if}
	{/each}
{/each}
