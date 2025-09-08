<script lang="ts">
  import { Node } from 'svelvet';

  function handleClick(e: CustomEvent) {
    const { node } = e.detail; // full node object
    node.bgColor.set('red');   // change background on click
  }
</script>

<Node
  id="55"
  on:nodeClicked={handleClick}
  let:grabHandle
  let:selected
  bgColor="lightgray"
  width={160}
  height={80}
>
  <!-- Only this element drags the node -->
  <div use:grabHandle class:selected class="my-component" style="padding:12px;">
    <span>{selected ? '✅ ' : ''}Click Me</span>
  </div>
</Node>

<style>
  /* You can style your inner content freely */
  .my-component {
    border: 1px solid #ccc;
    border-radius: 8px;
    user-select: none;
  }
  .selected {
    outline: 2px solid #666;
  }
</style>
