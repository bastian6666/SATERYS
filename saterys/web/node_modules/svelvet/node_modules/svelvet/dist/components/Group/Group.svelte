<script>import { setContext, getContext } from "svelte";
import { writable } from "svelte/store";
import { getRandomColor } from "../../utils";
export let width;
export let height;
export let position;
export let color = getRandomColor();
export let groupName;
const graph = getContext("graph");
const groupKey = `${groupName}/${graph.id}`;
setContext("group", groupKey);
const writablePosition = writable(position);
const groupBox = {
  group: writable(groupKey),
  dimensions: { width: writable(width), height: writable(height) },
  position: writablePosition,
  color: writable(color),
  moving: writable(false)
};
graph.groupBoxes.add(groupBox, groupKey);
graph.groups.update((groups) => {
  const newGroup = {
    parent: writable(groupBox),
    nodes: writable(/* @__PURE__ */ new Set([groupBox]))
  };
  groups[groupKey] = newGroup;
  return groups;
});
</script>

<slot />
