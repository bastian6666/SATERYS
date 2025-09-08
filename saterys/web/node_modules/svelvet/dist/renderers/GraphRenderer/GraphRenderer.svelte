<script>console.log("Componente GraphRenderer.svelte");
import GroupBoxRenderer from "../GroupBoxRenderer/GroupBoxRenderer.svelte";
import ZoomPanWrapper from "../../containers/ZoomPanWrapper/ZoomPanWrapper.svelte";
import { initialClickPosition, tracking } from "../../stores/CursorStore";
import { captureGroup, moveNodes } from "../../utils/movers";
import { getContext } from "svelte";
const graph = getContext("graph");
const snapTo = getContext("snapTo");
export let isMovable;
const activeGroup = graph.activeGroup;
const groups = graph.groups;
const initialNodePositions = graph.initialNodePositions;
const cursor = graph.cursor;
$:
  if ($activeGroup && $tracking) {
    moveNodes(graph, snapTo);
  }
function handleGroupClicked(event) {
  $tracking = true;
  const { groupName } = event.detail;
  $activeGroup = groupName;
  $initialClickPosition = $cursor;
  $initialNodePositions = captureGroup($groups[groupName].nodes);
}
</script>

<!--GroupBoxRenderer-This component renders the graphical representation of the groups in the graph. It listens for a groupClick event and, when triggered, invokes handleGroupClicked to initiate the logic for handling group selection and movement.
-->
<ZoomPanWrapper {isMovable}>
	<slot />
	<GroupBoxRenderer on:groupClick={handleGroupClicked} />
</ZoomPanWrapper>
