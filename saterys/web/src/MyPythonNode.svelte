<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Node } from 'svelvet';

  export let id: string;
  export let position = { x: 120, y: 120 };

  const dispatch = createEventDispatcher();

  let loading = false;
  let lastMessage = '';

  async function runPython() {
    loading = true;
    try {
      const res = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label: 'Hello from Svelte' })
      });
      const data = await res.json();
      lastMessage = `${data.result} @ ${data.serverTime}`;
      // Bubble a custom event so App.svelte can react (e.g., add a new node)
      dispatch('pythonResult', data);
    } catch (e) {
      lastMessage = 'Error calling Python';
      console.error(e);
    } finally {
      loading = false;
    }
  }
</script>

<Node id={id} bind:position label="Python Node" width={190} height={110}>
  <div style="display:flex; flex-direction:column; gap:8px; padding:10px;">
    <button on:click={runPython} disabled={loading}>
      {loading ? 'Running…' : 'Run Python'}
    </button>
    <small>{lastMessage}</small>
  </div>
</Node>

<style>
  button { padding: 6px 10px; border: 1px solid #777; border-radius: 6px; cursor: pointer; }
</style>
