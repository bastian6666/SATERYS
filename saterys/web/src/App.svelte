<script lang="ts">
  // @ts-ignore
  import { Svelvet, Node } from 'svelvet';
  import { onMount, tick, onDestroy} from 'svelte';


  // Leaflet
  // @ts-ignore
  import * as L from 'leaflet';
  import 'leaflet/dist/leaflet.css';

  // ----- Types -----
  type NodeData = {
    id: string;
    position: { x: number; y: number };
    label: string;
    type: string;     // backend op key
    args: any;        // JSON-serializable
  };
  type EdgeData = { id: string; source: string; target: string };
  type NodeType = { name: string; default_args: any };
  type LogLine = { nodeId: string; ok: boolean; text: string };

  // ----- Node/canvas geometry -----
  const NODE_W = 230;
  const NODE_H = 80;

  // Theme
  let theme: 'dark' | 'light' = 'dark';
  $: (document?.body && (document.body.dataset.theme = theme));

  // Start with ZERO nodes (changed)
  let nodes: NodeData[] = [];
  let nextNodeIndex = 1;
  let edges: EdgeData[] = [];
  let nextEdgeId = 1;
  let pendingSource: string | null = null;

  // Args editor buffer per node
  let argsText: Record<string, string> = {};

  // Available op types (optionally fetch from backend)
  let TYPES: NodeType[] = [
    { name: 'hello',        default_args: { name: 'world' } },
    { name: 'sum',          default_args: { nums: [1, 2, 3] } },
    { name: 'script',       default_args: { code: "print('hello')" } },
    { name: 'raster.input', default_args: { path: "" } },
    { name: 'ollama.ai',    default_args: { prompt: "Create a raster processing node", model: "llama3.2:latest" } },
  ];
  onMount(async () => {
    try {
      const r = await fetch('/node_types');
      const data = await r.json();
      if (Array.isArray(data?.types)) TYPES = data.types as NodeType[];
    } catch { /* backend optional */ }
  });

  // ----- Field schemas for nicer forms -----
  type Field =
    | { key: string; label: string; type: 'string'; placeholder?: string }
    | { key: string; label: string; type: 'number'; step?: number }
    | { key: string; label: string; type: 'boolean' }
    | { key: string; label: string; type: 'textarea'; placeholder?: string; rows?: number }
    | { key: string; label: string; type: 'array'; itemType?: 'string'|'number'; hint?: string }
    | { key: string; label: string; type: 'select'; options: string[] };

  const SCHEMAS: Record<string, Field[]> = {
    hello: [{ key: 'name', label: 'Name', type: 'string', placeholder: 'world' }],
    sum:   [{ key: 'nums', label: 'Numbers', type: 'array', itemType: 'number', hint: 'e.g., 1,2,3' }],
    script:[{ key: 'code', label: 'Code', type: 'textarea', rows: 8, placeholder: "print('hello')" }],
    'raster.input': [{ key: 'path', label: 'Raster path', type: 'string', placeholder: '/path/to.tif' }],
    'ollama.ai': [
      { key: 'prompt', label: 'AI Prompt', type: 'textarea', rows: 4, placeholder: 'Describe the workflow you want to create...' },
      { key: 'model', label: 'Model', type: 'string', placeholder: 'llama3.2:latest' },
      { key: 'ollama_host', label: 'OLLAMA Host', type: 'string', placeholder: 'http://localhost:11434' },
      { key: 'temperature', label: 'Temperature', type: 'number', step: 0.1 },
      { key: 'max_tokens', label: 'Max Tokens', type: 'number' }
    ],
  };

  function guessSchemaFromDefaults(def: any): Field[] {
    const fields: Field[] = [];
    if (!def || typeof def !== 'object') return fields;
    for (const [k, v] of Object.entries(def)) {
      if (typeof v === 'string')      fields.push({ key: k, label: k, type: 'string' });
      else if (typeof v === 'number') fields.push({ key: k, label: k, type: 'number' });
      else if (typeof v === 'boolean')fields.push({ key: k, label: k, type: 'boolean' });
      else if (Array.isArray(v))      fields.push({ key: k, label: k, type: 'array', itemType: typeof v[0] === 'number' ? 'number' : 'string' });
      else                             fields.push({ key: k, label: k, type: 'textarea' }); // fallback JSON-ish
    }
    return fields;
  }
  function schemaForType(t: string): Field[] {
    const known = SCHEMAS[t];
    if (known) return known;
    const def = TYPES.find(x => x.name === t)?.default_args;
    return guessSchemaFromDefaults(def ?? {});
  }

  // Init argsText
  $: {
    for (const n of nodes) {
      if (argsText[n.id] === undefined) {
        try { argsText[n.id] = JSON.stringify(n.args ?? {}, null, 2); }
        catch { argsText[n.id] = '{}'; }
      }
    }
  }

  // Prune edges if nodes removed
  $: {
    const ids = new Set(nodes.map(n => n.id));
    const pruned = edges.filter(e => ids.has(e.source) && ids.has(e.target));
    if (pruned.length !== edges.length) edges = pruned;
  }

  const nodeById = (id: string) => nodes.find(n => n.id === id);

  function addEdge(source: string, target: string) {
    if (!nodeById(source) || !nodeById(target) || source === target) return;
    if (edges.some(e => e.source === source && e.target === target)) return;
    edges = [...edges, { id: `e${nextEdgeId++}`, source, target }];
  }
  function deleteEdgeById(id: string) { edges = edges.filter(e => e.id !== id); }
  function deleteNode(id: string) {
    // Clean up overlay layer if it exists
    if (overlayLayers.has(id) && map && layerControl) {
      const layer = overlayLayers.get(id)!;
      map.removeLayer(layer);
      layerControl.removeLayer(layer);
      overlayLayers.delete(id);
    }
    nodes = nodes.filter(n => n.id !== id);
    delete argsText[id];
  }

  function activeGraph() {
    const involved = new Set<string>();
    for (const e of edges) { involved.add(e.source); involved.add(e.target); }
    const activeNodes = nodes.filter(n => involved.has(n.id));
    const set = new Set(activeNodes.map(n => n.id));
    const activeEdges = edges.filter(e => set.has(e.source) && set.has(e.target));
    return { activeNodes, activeEdges };
  }

  function topoOrder(nodeList: NodeData[], edgeList: EdgeData[]): string[] {
    const ids = nodeList.map(n => n.id);
    const idSet = new Set(ids);
    const adj = new Map<string, string[]>();
    const indeg = new Map<string, number>();
    for (const id of ids) { adj.set(id, []); indeg.set(id, 0); }
    for (const e of edgeList) {
      if (!idSet.has(e.source) || !idSet.has(e.target)) continue;
      adj.get(e.source)!.push(e.target);
      indeg.set(e.target, (indeg.get(e.target) || 0) + 1);
    }
    const q: string[] = [];
    for (const id of ids) if ((indeg.get(id) || 0) === 0) q.push(id);
    const order: string[] = [];
    while (q.length) {
      const u = q.shift()!;
      order.push(u);
      for (const v of adj.get(u)!) {
        indeg.set(v, (indeg.get(v) || 0) - 1);
        if ((indeg.get(v) || 0) === 0) q.push(v);
      }
    }
    return order;
  }

  // ----- Run pipeline -----
  let logs: LogLine[] = [];
  let running = false;
  let lastOutputs: Record<string, any> = {};

  // logs drawer visibility (hidden by default)
  let showLogs = false;

  // sidebar collapse
  let sidebarCollapsed = false;

  function pushLog(nodeId: string, ok: boolean, text: string) {
    logs = [...logs, { nodeId, ok, text }];
    if (showLogs) requestAnimationFrame(() => {
      const el = document.querySelector('.logs-body');
      if (el) (el as HTMLElement).scrollTop = (el as HTMLElement).scrollHeight;
    });
  }

  async function runNode(node: NodeData, inputs: any = {}) {
    const res = await fetch('/run_node', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nodeId: node.id,
        type: node.type,
        args: node.args ?? {},
        inputs
      })
    });
    const data = await res.json().catch(() => ({ ok: false, error: 'Bad JSON' }));
    return data as any;
  }

  async function runPipeline() {
    running = true;
    logs = [];
    lastOutputs = {};
    showLogs = true; // auto-open logs when running

    const { activeNodes, activeEdges } = activeGraph();
    if (activeNodes.length === 0) {
      pushLog('system', false, 'No connected nodes to run.');
      running = false;
      return;
    }

    const order = topoOrder(activeNodes, activeEdges);
    if (order.length !== activeNodes.length) {
      pushLog('system', false, 'Warning: cycle detected; running partial order.');
    }

    const upstreamOf: Record<string, string[]> = {};
    for (const e of activeEdges) (upstreamOf[e.target] ??= []).push(e.source);

    for (const id of order) {
      const n = nodeById(id)!;
      const inputs: Record<string, any> = {};
      for (const up of upstreamOf[id] ?? []) inputs[up] = lastOutputs[up];

      pushLog(id, true, '▶ Running…');

      try {
        const data = await runNode(n, inputs);

        if (Array.isArray(data?.logs)) for (const line of data.logs) pushLog(id, true, String(line));
        if (typeof data?.stdout === 'string' && data.stdout.trim()) {
          for (const line of data.stdout.split(/\r?\n/)) if (line.trim()) pushLog(id, true, line);
        }

        if (data?.ok) {
          const out = data.output ?? {};
          lastOutputs[id] = out;
          const text = typeof out === 'string' ? out : (out.text ?? JSON.stringify(out));
          pushLog(id, true, `✅ ${text}`);
        } else {
          pushLog(id, false, `❌ ${data?.error || 'Unknown error'}`);
        }
      } catch (e: any) {
        pushLog(id, false, `❌ Exception: ${e?.message || e}`);
      }
    }
    running = false;
  }

  // ----- Node add/connect -----
  function addNode() {
    const id = `n${nextNodeIndex++}`;
    const t = TYPES[0] || { name: 'hello', default_args: { name: id } };
    const x = 120 + (nodes.length % 6) * 260;
    const y = 140 + Math.floor(nodes.length / 6) * 140;
    const defaults = JSON.parse(JSON.stringify(t.default_args || {}));
    const label = `${t.name} (${id})`;
    nodes = [...nodes, { id, position: { x, y }, label, type: t.name, args: defaults }];
    argsText[id] = JSON.stringify(defaults, null, 2);
  }

  function clickOutput(nodeId: string) { pendingSource = nodeId; }
  function clickInput(targetId: string) { if (pendingSource) addEdge(pendingSource, targetId); pendingSource = null; }
  function cancelPending() { pendingSource = null; }

  const leftX  = (n: NodeData) => n.position.x;
  const rightX = (n: NodeData) => n.position.x + NODE_W;
  const midY   = (n: NodeData) => n.position.y + NODE_H / 2;

  let positionsKey: string = '';
  $: positionsKey = nodes.map(n => `${n.id}:${n.position.x},${n.position.y}`).join('|');

  // ----- Canvas viewport sizing (fills available space) -----
  let canvasWrapEl: HTMLDivElement | null = null;
  let viewW = 1200;
  let viewH = 650;
  let canvasRO: ResizeObserver | null = null;

  // ----- Resizable split pane -----
  let splitRatio = 0.66; // Canvas takes 66% by default
  let dragging = false;
  let workAreaEl: HTMLDivElement | null = null;

  function handleSplitDrag(e: MouseEvent) {
    if (!dragging || !workAreaEl) return;
    
    const rect = workAreaEl.getBoundingClientRect();
    const newRatio = (e.clientX - rect.left) / rect.width;
    splitRatio = Math.max(0.2, Math.min(0.8, newRatio)); // Limit between 20% and 80%
  }

  function startDrag() {
    dragging = true;
    document.addEventListener('mousemove', handleSplitDrag);
    document.addEventListener('mouseup', stopDrag);
  }

  function stopDrag() {
    dragging = false;
    document.removeEventListener('mousemove', handleSplitDrag);
    document.removeEventListener('mouseup', stopDrag);
  }

  function watchCanvasSize() {
    if (!canvasWrapEl) return;
    if (canvasRO) canvasRO.disconnect();
    canvasRO = new ResizeObserver(() => {
      if (!canvasWrapEl) return;
      viewW = Math.max(320, Math.floor(canvasWrapEl.clientWidth  - 1));
      viewH = Math.max(240, Math.floor(canvasWrapEl.clientHeight - 1));
    });
    canvasRO.observe(canvasWrapEl);
  }

  // ----- Leaflet map (always-on) -----
  let map: L.Map | null = null;
  let overlayLayers: Map<string, L.TileLayer> = new Map();
  let layerControl: L.Control.Layers | null = null;
  let mapEl: HTMLDivElement | null = null;
  let mapContainerEl: HTMLDivElement | null = null;
  let ro: ResizeObserver | null = null;

  function setupResizeObserver() {
    if (!map || !mapContainerEl) return;
    if (ro) ro.disconnect();
    ro = new ResizeObserver(() => {
      requestAnimationFrame(() => map && map.invalidateSize());
    });
    ro.observe(mapContainerEl);
  }

  function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
    requestAnimationFrame(() => map?.invalidateSize());
  }

  onMount(() => {
    let destroyed = false;
    const onWin = () => map && map.invalidateSize();

    Promise.resolve().then(async () => {
      await tick();
      if (destroyed) return;

      // Canvas ResizeObserver
      watchCanvasSize();

      // Map init (once)
      if (!map && mapEl) {
        map = L.map(mapEl, { zoomControl: true, attributionControl: false }).setView([0, 0], 2);

        const baseLayers: Record<string, L.TileLayer> = {
          "🗺️ OpenStreetMap": L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            opacity: 0.9, minZoom: 1, maxZoom: 22, attribution: '© OpenStreetMap contributors'
          }),
          "🌌 OSM (Dark-ish)": L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            opacity: 0.95, minZoom: 1, maxZoom: 22, attribution: '© OpenStreetMap, © CartoDB'
          }),
          "🛰️ Esri World Imagery": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            opacity: 1.0, minZoom: 1, maxZoom: 19, attribution: 'Tiles © Esri'
          }),
          "🗺️ Carto Positron": L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            opacity: 0.95, minZoom: 1, maxZoom: 22, attribution: '© OpenStreetMap, © CartoDB'
          }),
          "⛰️ OpenTopoMap": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            opacity: 0.95, minZoom: 1, maxZoom: 17, attribution: '© OpenStreetMap, © OpenTopoMap'
          })
        };

        baseLayers["🛰️ Esri World Imagery"].addTo(map); // start with imagery

        layerControl = L.control.layers(baseLayers, {}, { position: 'topright', collapsed: false });
        layerControl.addTo(map);

        setupResizeObserver();
        window.addEventListener('resize', onWin);
      }
    });

    return () => {
      destroyed = true;
      window.removeEventListener('resize', onWin);
      ro?.disconnect();
      canvasRO?.disconnect();
    };
  });

  function getRasterPathForNode(n: NodeData, i: number): string | null {
    const out = lastOutputs[n.id];
    if (out && typeof out === 'object' && out.type === 'raster' && out.path) return out.path;
    if (n.type === 'raster.input' && typeof nodes[i].args?.path === 'string') return nodes[i].args.path;
    return null;
  }

  async function previewNode(n: NodeData, i: number) {
    if (!map || !layerControl) { alert('Map not ready yet.'); return; }
    const pth = getRasterPathForNode(n, i);
    if (!pth) { alert('No raster path available. Run the pipeline or set args.path for raster.input.'); return; }

    const id = n.id;
    await fetch('/preview/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, path: pth })
    });

    const url = `/preview/tile/${id}/{z}/{x}/{y}.png`;
    const layerName = `${n.label} (${n.id})`;

    if (overlayLayers.has(id)) {
      const existingLayer = overlayLayers.get(id)!;
      map.removeLayer(existingLayer);
      layerControl.removeLayer(existingLayer);
      overlayLayers.delete(id);
    }

    const newLayer = L.tileLayer(url, { tms: false, opacity: 0.8, maxZoom: 22 });
    overlayLayers.set(id, newLayer);
    newLayer.addTo(map);
    layerControl.addOverlay(newLayer, layerName);

    const b = await fetch(`/preview/bounds/${id}`).then(r => r.json());
    const [west, south, east, north] = b.bounds;
    const bounds = L.latLngBounds([south, west], [north, east]);
    map.fitBounds(bounds, { padding: [10, 10] });
  }

  function clearOverlayLayers() {
    if (!map || !layerControl) return;
    for (const [, layer] of overlayLayers) {
      map.removeLayer(layer);
      layerControl.removeLayer(layer);
    }
    overlayLayers.clear();
  }

  // -------- Modal: edit args (form + advanced JSON) --------
  let editingNode: NodeData | null = null;
  let editingBuffer = "";
  let editingSchema: Field[] = [];
  let editingForm: Record<string, any> = {};
  let showAdvancedJSON = false;

  function openArgsModal(n: NodeData) {
    editingNode = n;
    editingSchema = schemaForType(n.type);
    editingForm = {};
    // Seed form values from node args or defaults
    const defaults = TYPES.find(t => t.name === n.type)?.default_args ?? {};
    const src = { ...defaults, ...(n.args ?? {}) };
    for (const f of editingSchema) {
      editingForm[f.key] = src[f.key];
    }
    editingBuffer = JSON.stringify(n.args ?? {}, null, 2);
    showAdvancedJSON = false;
  }

  function applyFormToNode() {
    if (!editingNode) return;
    const out: any = {};
    // Build args according to schema
    for (const f of editingSchema) {
      let v = editingForm[f.key];
      if (f.type === 'number') v = Number(v);
      if (f.type === 'array') {
        if (Array.isArray(v)) out[f.key] = v;
        else if (typeof v === 'string') {
          const parts = v.split(',').map(s => s.trim()).filter(Boolean);
          out[f.key] = (f.itemType === 'number') ? parts.map(Number) : parts;
        } else {
          out[f.key] = [];
        }
        continue;
      }
      if (f.type === 'boolean') v = !!v;
      out[f.key] = v;
    }
    editingNode.args = out;
    argsText[editingNode.id] = JSON.stringify(out, null, 2);
  }

  function saveArgsModal() {
    if (!editingNode) return;
    if (showAdvancedJSON) {
      try {
        const parsed = JSON.parse(editingBuffer || "{}");
        editingNode.args = parsed;
        argsText[editingNode.id] = JSON.stringify(parsed, null, 2);
        editingNode = null;
      } catch {
        alert("Invalid JSON");
      }
    } else {
      applyFormToNode();
      editingNode = null;
    }
  }

  // Utilities for node positions
  const nodeByIdStrict = (id: string): NodeData => {
    const n = nodes.find(n => n.id === id);
    if (!n) throw new Error(`Node not found: ${id}`);
    return n;
  };


  function taRows(f: Field): number {
  return (f as any).rows ?? 6;
}
function taPlaceholder(f: Field): string {
  return (f as any).placeholder ?? '';
}
function arrHint(f: Field): string {
  return (f as any).hint ?? 'comma-separated';
}
function arrItemType(f: Field): string {
  return (f as any).itemType ?? 'values';
}
function selectOptions(f: Field): string[] {
  return (f as any).options ?? [];
}

// ===== Server run history / logs (polling) =====
type RunSummary = {
  id: string; job_id: string;
  started_at: string;
  finished_at?: string | null;
  status: 'running' | 'success' | 'error';
};
type RunDetail = RunSummary & { logs: string[] };

let runPollTimer: any = null;

async function openJobLogs(jobId: string) {
  showLogs = true;  // open the bottom drawer you already have
  logs = [];        // clear current UI logs
  await pollLatestRun(jobId);
  if (runPollTimer) clearInterval(runPollTimer);
  runPollTimer = setInterval(() => pollLatestRun(jobId), 1000);
}

async function pollLatestRun(jobId: string) {
  try {
    const list: RunSummary[] = await fetch(`/pipeline/schedules/${jobId}/runs`).then(r => r.json());
    if (!Array.isArray(list) || list.length === 0) {
      logs = [{ nodeId: 'system', ok: true, text: '(no runs yet)' }];
      return;
    }
    const latest = list[0]; // newest first
    const det: RunDetail = await fetch(`/pipeline/schedules/runs/${latest.id}`).then(r => r.json());
    logs = det.logs.map(line => ({
      nodeId: det.status === 'running' ? 'run' : (det.status === 'success' ? 'ok' : 'err'),
      ok: !/❌|exception/i.test(line),
      text: line
    }));
    // stop polling once finished
    if (det.status !== 'running' && runPollTimer) {
      clearInterval(runPollTimer);
      runPollTimer = null;
    }
  } catch (e) {
    logs = [{ nodeId: 'system', ok: false, text: 'Failed to fetch run logs' }];
  }
}

// stop polling if the drawer is closed
$: if (!showLogs && runPollTimer) { clearInterval(runPollTimer); runPollTimer = null; }

// cleanup on hot reload / navigate
onDestroy(() => { if (runPollTimer) clearInterval(runPollTimer); });


// ===== PIPELINE SCHEDULING (entire graph) =====
type ScheduleMode = 'once' | 'interval' | 'cron';
type PipeNode = { id: string; type: string; args: any };
type PipeEdge = { source: string; target: string };
type PipelineScheduleCreate = {
  mode: ScheduleMode;
  run_at?: string;
  seconds?: number;
  minutes?: number;
  hours?: number;
  cron?: string;
  graph: { nodes: PipeNode[]; edges: PipeEdge[] };
};
type Schedule = { id: string; next_run_time?: string | null };

let showPipelineScheduleModal = false;
let scheduleMode: ScheduleMode = 'once';
let scheduleLocalDateTime = '';
let scheduleHours = 0, scheduleMinutes = 0, scheduleSeconds = 0;
let scheduleCron = '0 5 * * *';
let scheduleSubmitting = false;
let scheduleError = '';
let schedules: Schedule[] = [];

function toLocal(ts?: string | null) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleString();
}

function openPipelineSchedule() {
  const { activeNodes } = activeGraph();
  if (activeNodes.length === 0) {
    alert('No connected nodes to schedule. Connect nodes with edges first.');
    return;
  }
  showPipelineScheduleModal = true;
  scheduleMode = 'once';
  scheduleLocalDateTime = '';
  scheduleHours = scheduleMinutes = scheduleSeconds = 0;
  scheduleCron = '0 5 * * *';
  scheduleError = '';
}

function graphSnapshot() {
  const { activeNodes, activeEdges } = activeGraph();
  const nodesOut: PipeNode[] = activeNodes.map(n => ({ id: n.id, type: n.type, args: n.args ?? {} }));
  const edgesOut: PipeEdge[] = activeEdges.map(e => ({ source: e.source, target: e.target }));
  return { nodes: nodesOut, edges: edgesOut };
}

async function createPipelineSchedule() {
  const g = graphSnapshot();
  if (g.nodes.length === 0) { scheduleError = 'Nothing to schedule (empty graph).'; return; }

  const payload: PipelineScheduleCreate = { mode: scheduleMode, graph: g };

  if (scheduleMode === 'once') {
    if (!scheduleLocalDateTime) { scheduleError = 'Please pick a date & time.'; return; }
    payload.run_at = new Date(scheduleLocalDateTime).toISOString(); // local → UTC
  } else if (scheduleMode === 'interval') {
    payload.hours = Number(scheduleHours) || 0;
    payload.minutes = Number(scheduleMinutes) || 0;
    payload.seconds = Number(scheduleSeconds) || 0;
    if (!(payload.hours || payload.minutes || payload.seconds)) {
      scheduleError = 'Interval must be > 0.'; return;
    }
  } else { // cron
    payload.cron = (scheduleCron || '').trim();
    if (!payload.cron) { scheduleError = 'Cron expression is required.'; return; }
  }

  scheduleSubmitting = true; scheduleError = '';
  try {
    const res = await fetch('/pipeline/schedules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await res.json();
    showPipelineScheduleModal = false;
    await refreshSchedules();
  } catch (e: any) {
    scheduleError = `Failed to create schedule: ${e?.message || e}`;
  } finally {
    scheduleSubmitting = false;
  }
}

async function refreshSchedules() {
  try {
    const r = await fetch('/pipeline/schedules');
    if (r.ok) { schedules = await r.json(); return; }
  } catch {}
  // (optional fallback if you keep a generic list endpoint)
  try {
    const r2 = await fetch('/schedules');
    if (r2.ok) schedules = await r2.json();
  } catch {}
}
async function deleteSchedule(jobId: string) {
  await fetch(`/pipeline/schedules/${jobId}`, { method: 'DELETE' }).catch(()=>{});
  await refreshSchedules();
}
async function pauseSchedule(jobId: string) {
  await fetch(`/pipeline/schedules/${jobId}/pause`, { method: 'POST' }).catch(()=>{});
  await refreshSchedules();
}
async function resumeSchedule(jobId: string) {
  await fetch(`/pipeline/schedules/${jobId}/resume`, { method: 'POST' }).catch(()=>{});
  await refreshSchedules();
}
async function runNow(jobId: string) {
  await fetch(`/pipeline/schedules/${jobId}/run-now`, { method: 'POST' }).catch(()=>{});
}

// kick once on load
onMount(async () => { await refreshSchedules().catch(()=>{}); });

// ===== WORKFLOW MANAGEMENT (save/load flows) =====
let savedWorkflows: Array<{name: string; description: string; created_at: string}> = [];
let showSaveModal = false;
let showLoadModal = false;
let saveWorkflowName = '';
let saveWorkflowDescription = '';

async function loadSavedWorkflows() {
  try {
    const response = await fetch('/workflows');
    const data = await response.json();
    savedWorkflows = data.workflows || [];
  } catch (e) {
    console.error('Failed to load workflows:', e);
  }
}

function openSaveModal() {
  saveWorkflowName = '';
  saveWorkflowDescription = '';
  showSaveModal = true;
}

function openLoadModal() {
  loadSavedWorkflows();
  showLoadModal = true;
}

async function saveCurrentWorkflow() {
  if (!saveWorkflowName.trim()) {
    alert('Please enter a workflow name');
    return;
  }

  try {
    const response = await fetch('/workflows', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: saveWorkflowName,
        description: saveWorkflowDescription,
        nodes: nodes.map(n => ({
          id: n.id,
          type: n.type,
          position: n.position,
          label: n.label,
          args: n.args
        })),
        edges: edges.map(e => ({
          id: e.id,
          source: e.source,
          target: e.target
        }))
      })
    });

    const result = await response.json();
    if (result.ok) {
      showSaveModal = false;
      alert(`Workflow "${saveWorkflowName}" saved successfully!`);
    } else {
      alert(`Failed to save workflow: ${result.error}`);
    }
  } catch (e) {
    alert(`Error saving workflow: ${e}`);
  }
}

async function loadWorkflow(workflowName: string) {
  try {
    const response = await fetch(`/workflows/${workflowName}`);
    const result = await response.json();
    
    if (result.ok && result.workflow) {
      const workflow = result.workflow;
      
      // Clear current workflow
      nodes = [];
      edges = [];
      argsText = {};
      
      // Load nodes
      nodes = workflow.nodes.map((n: any) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        label: n.label,
        args: n.args || {}
      }));
      
      // Load edges
      edges = workflow.edges.map((e: any) => ({
        id: e.id,
        source: e.source,
        target: e.target
      }));
      
      // Initialize args text
      for (const n of nodes) {
        argsText[n.id] = JSON.stringify(n.args || {}, null, 2);
      }
      
      showLoadModal = false;
      alert(`Workflow "${workflowName}" loaded successfully!`);
    } else {
      alert(`Failed to load workflow: ${result.error || 'Unknown error'}`);
    }
  } catch (e) {
    alert(`Error loading workflow: ${e}`);
  }
}

async function deleteWorkflow(workflowName: string) {
  if (!confirm(`Are you sure you want to delete workflow "${workflowName}"?`)) {
    return;
  }
  
  try {
    const response = await fetch(`/workflows/${workflowName}`, { method: 'DELETE' });
    const result = await response.json();
    
    if (result.ok) {
      loadSavedWorkflows(); // Refresh list
      alert(`Workflow "${workflowName}" deleted successfully!`);
    } else {
      alert(`Failed to delete workflow: ${result.error}`);
    }
  } catch (e) {
    alert(`Error deleting workflow: ${e}`);
  }
}

// ===== OLLAMA AI CHAT INTERFACE =====
let showAIChat = false;
let aiChatPrompt = '';
let aiChatResponse = '';
let aiGenerating = false;
let ollamaStatus = { ok: false, status: 'unknown', available_models: [] };

async function checkOllamaStatus() {
  try {
    const response = await fetch('/ollama/status');
    ollamaStatus = await response.json();
  } catch (e) {
    ollamaStatus = { ok: false, status: 'error', message: 'Connection failed' };
  }
}

function openAIChat() {
  showAIChat = true;
  checkOllamaStatus();
}

async function generateWithAI() {
  if (!aiChatPrompt.trim()) {
    alert('Please enter a prompt');
    return;
  }
  
  aiGenerating = true;
  aiChatResponse = '';
  
  try {
    const response = await fetch('/ollama/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: aiChatPrompt,
        model: 'llama3.2:latest',
        temperature: 0.7,
        max_tokens: 1000
      })
    });
    
    const result = await response.json();
    
    if (result.success && result.workflow_suggestion) {
      // AI provided a structured workflow suggestion
      const suggestion = result.workflow_suggestion;
      aiChatResponse = `${result.ai_response}\n\n--- Suggested Workflow ---\n${JSON.stringify(suggestion, null, 2)}`;
      
      // Ask user if they want to apply the suggestion
      if (confirm('AI has generated a workflow suggestion. Would you like to add it to the canvas?')) {
        applyAISuggestion(suggestion);
      }
    } else if (result.ai_response) {
      // AI provided a text response
      aiChatResponse = result.ai_response;
    } else {
      aiChatResponse = `Error: ${result.error || 'Unknown error'}`;
    }
  } catch (e) {
    aiChatResponse = `Error: ${e}`;
  } finally {
    aiGenerating = false;
  }
}

function applyAISuggestion(suggestion: any) {
  if (!suggestion.nodes || !Array.isArray(suggestion.nodes)) {
    alert('Invalid workflow suggestion format');
    return;
  }
  
  // Find an empty space in the canvas
  const startX = 120 + (nodes.length % 6) * 260;
  const startY = 140 + Math.floor(nodes.length / 6) * 140;
  
  const nodeIdMap = new Map();
  
  // Add nodes from suggestion
  suggestion.nodes.forEach((suggestedNode: any, index: number) => {
    const newId = `ai_n${nextNodeIndex++}`;
    nodeIdMap.set(suggestedNode.id || index, newId);
    
    const x = startX + (index % 3) * 260;
    const y = startY + Math.floor(index / 3) * 140;
    
    const nodeType = TYPES.find(t => t.name === suggestedNode.type) || TYPES[0];
    
    nodes = [...nodes, {
      id: newId,
      position: { x, y },
      label: suggestedNode.label || `${suggestedNode.type} (${newId})`,
      type: suggestedNode.type,
      args: suggestedNode.args || nodeType.default_args || {}
    }];
    
    argsText[newId] = JSON.stringify(suggestedNode.args || nodeType.default_args || {}, null, 2);
  });
  
  // Add edges if provided
  if (suggestion.edges && Array.isArray(suggestion.edges)) {
    suggestion.edges.forEach((suggestedEdge: any) => {
      const sourceId = nodeIdMap.get(suggestedEdge.source);
      const targetId = nodeIdMap.get(suggestedEdge.target);
      
      if (sourceId && targetId) {
        edges = [...edges, {
          id: `ai_e${nextEdgeId++}`,
          source: sourceId,
          target: targetId
        }];
      }
    });
  }
  
  showAIChat = false;
  aiChatPrompt = '';
  alert('AI workflow suggestion applied to canvas!');
}

// Load workflows on mount
onMount(async () => { 
  await refreshSchedules().catch(()=>{});
  await loadSavedWorkflows().catch(()=>{});
});


</script>

<!-- APP ROOT -->
<div class="app-root">
  <!-- Header (styled like manual labeler) -->
  <header class="topbar glass">
    <div class="left">
      <button class="icon-btn ghost" title="Toggle sidebar" on:click={toggleSidebar}>
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
      </button>
      <div class="brand">
        <span class="title">SATERYS</span>
      </div>
    </div>

    <div class="center">
      <div class="hint">Build pipelines — click a node’s ◀ / ▶ to connect</div>
    </div>

    <div class="right">
      <button class="icon-btn" title={running ? 'Running…' : 'Run pipeline'} on:click={runPipeline} disabled={running}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>
        <span>Run</span>
      </button>
      <button class="icon-btn" title="Schedule pipeline" on:click={openPipelineSchedule}>
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
        <path d="M8 7V4m8 3V4M5 11h14M7 21h10a2 2 0 002-2V8a2 2 0 00-2-2H7a2 2 0 00-2 2v11a2 2 0 002 2zm5-6v-3" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
      </svg>
      <span>Schedule</span>
      </button>
      <button class="icon-btn" title="Toggle logs" on:click={() => showLogs = !showLogs}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M4 5h16a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V7a2 2 0 012-2zm2 4l3 3-3 3m5 0h5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>Logs</span>
      </button>
      <button class="icon-btn" title="Clear map layers" on:click={clearOverlayLayers} disabled={overlayLayers.size === 0}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M12 3l9 5-9 5-9-5 9-5zm0 8l9 5-9 5-9-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/></svg>
        <span>Layers</span>
      </button>
      <button class="icon-btn" title="Toggle theme" on:click={() => theme = theme === 'dark' ? 'light' : 'dark'}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
        <span>{theme === 'dark' ? 'Dark' : 'Light'}</span>
      </button>
      <button class="icon-btn" title="AI Chat" on:click={openAIChat}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>AI Chat</span>
      </button>
      <button class="icon-btn" title="Save workflow" on:click={openSaveModal}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="17,21 17,13 7,13 7,21" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="7,3 7,8 15,8" stroke="currentColor" stroke-width="2" fill="none"/></svg>
        <span>Save</span>
      </button>
      <button class="icon-btn" title="Load workflow" on:click={openLoadModal}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" fill="none"/><line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/><line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/><polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2" fill="none"/></svg>
        <span>Load</span>
      </button>
      <button class="icon-btn primary" title="Add node" on:click={addNode}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
        <span>Add</span>
      </button>
    </div>
  </header>

  <!-- Main layout -->
  <div class="main" data-collapsed={sidebarCollapsed ? 'true' : 'false'}>
    <!-- Collapsible Sidebar -->
    <aside class="sidebar" data-collapsed={sidebarCollapsed ? 'true' : 'false'}>
      <div class="section">
        <div class="section-title">
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M5 12h14M12 5v14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
          <span class="txt">Tools</span>
        </div>
        <div class="tool-list">
          <button class="tool" on:click={addNode} title="Add node">
            <svg viewBox="0 0 24 24" width="16" height="16"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
            <span class="txt">Add Node</span>
          </button>
          <button class="tool" on:click={runPipeline} disabled={running} title="Run pipeline">
            <svg viewBox="0 0 24 24" width="16" height="16"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>
            <span class="txt">{running ? 'Running…' : 'Run'}</span>
          </button>
          <button class="tool" on:click={clearOverlayLayers} disabled={overlayLayers.size === 0} title="Clear overlay layers">
            <svg viewBox="0 0 24 24" width="16" height="16"><path d="M12 3l9 5-9 5-9-5 9-5zm0 8l9 5-9 5-9-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/></svg>
            <span class="txt">Clear Layers</span>
          </button>
          <button class="tool" on:click={() => theme = theme === 'dark' ? 'light' : 'dark'} title="Toggle theme">
            <svg viewBox="0 0 24 24" width="16" height="16"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
            <span class="txt">Theme: {theme}</span>
          </button>
        </div>
      </div>

      <div class="section">
        <div class="section-title">
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M3 12l7-7 4 4 7-7" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span class="txt">Edges</span>
        </div>
        <div class="edge-chips">
          {#if edges.length === 0}
            <div class="muted small txt">(none)</div>
          {:else}
            {#each edges as e (e.id)}
              <span class="edge-pill" title="Click × to remove">
                {e.source}→{e.target}
                <button class="pill-x" on:click={() => deleteEdgeById(e.id)} aria-label="Remove edge">×</button>
              </span>
            {/each}
          {/if}
        </div>
        {#if pendingSource}
          <div class="pending small">
            <span class="txt">connecting from <code>{pendingSource}</code> — click a node’s ◀ to finish</span>
            <button class="pill-x" on:click={cancelPending}>cancel</button>
          </div>
        {/if}
      </div>

      <div class="section">
  <div class="section-title">
    <svg viewBox="0 0 24 24" width="16" height="16"><path d="M6 6h12v12H6zM9 3h6M3 9h6M15 21h6M3 15h6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
    <span class="txt">Schedules</span>
    <button class="pill-x" on:click={refreshSchedules} title="Refresh">↻</button>
  </div>

  {#if schedules.length === 0}
    <div class="muted small txt">(no scheduled jobs)</div>
  {:else}
    <div class="tool-list">
      {#each schedules as j (j.id)}
  <div class="tool schedule-card">
    <div class="schedule-head">
      <div class="schedule-date">
        <time datetime={j.next_run_time}>{toLocal(j.next_run_time)}</time>
      </div>
    </div>

    <div class="schedule-actions">
      <!-- Run now + open logs immediately -->
      <button class="pill-x" title="Run now" on:click={() => { runNow(j.id); openJobLogs(j.id); }}>Run now</button>

      <!-- Pause / Resume -->
      <button class="pill-x" title="Pause"  on:click={() => pauseSchedule(j.id)}>Pause</button>
      <button class="pill-x" title="Resume" on:click={() => resumeSchedule(j.id)}>Resume</button>

      <!-- Text-only Logs button -->
      <button class="pill-x" title="Logs" on:click={() => openJobLogs(j.id)}>Logs</button>

      <!-- Delete -->
      <button class="pill-x" title="Delete" on:click={() => deleteSchedule(j.id)}>Delete</button>
    </div>
  </div>
{/each}
    </div>
  {/if}
</div>

    </aside>

    

    <!-- Work area: nodes + map -->
    <div class="work" bind:this={workAreaEl}>
      <div class="split" style="grid-template-columns: {splitRatio * 100}% 4px {(1 - splitRatio) * 100}%;">
        <div class="canvas-container" bind:this={canvasWrapEl}>
          <Svelvet width={viewW} height={viewH} {theme}>
          {#each nodes as n, i (n.id)}
            <Node id={n.id} bind:position={nodes[i].position} width={NODE_W} height={NODE_H} let:selected let:grabHandle>
              <div class="node" use:grabHandle aria-selected={selected ? 'true' : 'false'}>
                <div class="node-title">{n.label}</div>

                <!-- handles -->
                <button class="dot in"  title="input"  on:click={() => clickInput(n.id)} />
                <button class="dot out" title="output" on:click={() => clickOutput(n.id)} aria-pressed={pendingSource === n.id} />

                <!-- delete -->
                <button class="node-del" title="delete node" on:click={() => deleteNode(n.id)}>🗑</button>

                <!-- type + args -->
                <div class="node-config">
                  <select bind:value={nodes[i].type} on:change={() => {
                    const t = TYPES.find(tt => tt.name === nodes[i].type);
                    const defaults = t?.default_args ?? {};
                    nodes[i].args = JSON.parse(JSON.stringify(defaults));
                    nodes[i].label = `${nodes[i].type} (${n.id})`;
                    argsText[n.id] = JSON.stringify(nodes[i].args, null, 2);
                  }}>
                    {#each TYPES as t}
                      <option value={t.name}>{t.name}</option>
                    {/each}
                  </select>

                  <!-- field editor (modal) -->
                  <button class="edit-btn" on:click={() => openArgsModal(n)}>⚙</button>

                  <!-- map preview -->
                  <button class="preview-btn" title="Preview on map" on:click={() => previewNode(n, i)}>👁</button>
                  <button
                      class="runone-btn"
                      title="Run this node only"
                      on:click={async () => {
                        try {
                          // Call the same endpoint used in the pipeline, but only for this node.
                          const data = await runNode(n, {});   // inputs can be empty for manual_labeler
                          showLogs = true;                     // open logs drawer
                          pushLog(n.id, !!data?.ok, data?.ok
                            ? (data?.output?.message || 'Started')
                            : (data?.error || 'Error'));
                        } catch (e) {
                          pushLog(n.id, false, `Exception: ${
                            typeof e === 'object' && e !== null && 'message' in e
                              ? e.message
                              : String(e)
                          }`);
                          showLogs = true;
                        }
                      }}>
                      ▶
                    </button>
                </div>
              </div>
            </Node>
          {/each}

          <!-- Edges overlay (fixed duplicate loop bug) -->
          <svg class="edges-overlay" viewBox={`0 0 ${viewW} ${viewH}`} preserveAspectRatio="none">
            {#key positionsKey}
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" />
                </marker>
              </defs>
              {#each edges as e (e.id)}
                {#if nodeById(e.source) && nodeById(e.target)}
                  {@const s = nodeByIdStrict(e.source)}
                  {@const t = nodeByIdStrict(e.target)}
                  <path
                    d={`M ${rightX(s)} ${midY(s)}
                        C ${rightX(s)+60} ${midY(s)},
                          ${leftX(t)-60} ${midY(t)},
                          ${leftX(t)} ${midY(t)}`}
                    class="cable"
                    marker-end="url(#arrow)"
                  />
                {/if}
              {/each}
            {/key}
          </svg>
          </Svelvet>
        </div>
        
        <!-- Drag handle -->
        <div class="drag-handle" on:mousedown={startDrag} title="Drag to resize"></div>

        <!-- RIGHT: map viewer -->
        <div class="right" bind:this={mapContainerEl}>
          <div bind:this={mapEl} class="map"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Args Modal (Form + Advanced JSON) -->
  {#if editingNode}
    <div class="modal-backdrop" on:click={() => editingNode = null}></div>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-head">
        <h3>Edit Args — {editingNode.label}</h3>
        <div class="seg">
          <button class:seg-active={!showAdvancedJSON} on:click={() => showAdvancedJSON = false}>Form</button>
          <button class:seg-active={showAdvancedJSON} on:click={() => showAdvancedJSON = true}>Advanced JSON</button>
        </div>
      </div>

      {#if !showAdvancedJSON}
        <div class="form-grid">
          {#each editingSchema as f}
            <div class="form-row">
              <label>{f.label}</label>
              {#if f.type === 'string'}
                <input type="text" bind:value={editingForm[f.key]} placeholder={f.placeholder ?? ''} />
              {:else if f.type === 'number'}
                <input type="number" bind:value={editingForm[f.key]} step={f.step ?? 1} />
              {:else if f.type === 'boolean'}
                <label class="switch">
                  <input type="checkbox" bind:checked={editingForm[f.key]} />
                  <span></span>
                </label>
              {:else if f.type === 'textarea'}
                <textarea rows={taRows(f)}
          bind:value={editingForm[f.key]}
          placeholder={taPlaceholder(f)}></textarea>
              {:else if f.type === 'array'}
                <input type="text" bind:value={editingForm[f.key]} placeholder={arrHint(f)} />
                <small class="muted">Comma-separated {arrItemType(f)}</small>
              {:else if f.type === 'select'}
                <select bind:value={editingForm[f.key]}>
                {#each selectOptions(f) as opt}
                  <option value={opt}>{opt}</option>
                {/each}
              </select>

              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <textarea class="json-area" bind:value={editingBuffer}></textarea>
      {/if}

      <div class="modal-actions">
        <button class="btn" on:click={() => editingNode = null}>Cancel</button>
        <button class="btn primary" on:click={saveArgsModal}>Save</button>
      </div>
    </div>
  {/if}
  {#if showPipelineScheduleModal}
  <div class="modal-backdrop" on:click={() => showPipelineScheduleModal = false}></div>
  <div class="modal" on:click|stopPropagation>
    <div class="modal-head">
      <h3>Schedule Pipeline (active connected graph)</h3>
    </div>

    <div class="form-grid">
      <div class="form-row">
        <label>Mode</label>
        <select bind:value={scheduleMode}>
          <option value="once">Once</option>
          <option value="interval">Interval</option>
          <option value="cron">Cron</option>
        </select>
      </div>

      {#if scheduleMode === 'once'}
        <div class="form-row">
          <label>Date & time (your local)</label>
          <input type="datetime-local" bind:value={scheduleLocalDateTime} />
          <small class="muted">Stored & executed in UTC on the server.</small>
        </div>
      {:else if scheduleMode === 'interval'}
        <div class="form-row">
          <label>Interval</label>
          <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:8px;">
            <input type="number" min="0" placeholder="hours" bind:value={scheduleHours}/>
            <input type="number" min="0" placeholder="minutes" bind:value={scheduleMinutes}/>
            <input type="number" min="0" placeholder="seconds" bind:value={scheduleSeconds}/>
          </div>
          <small class="muted">At least one of hours/minutes/seconds must be &gt; 0.</small>
        </div>
      {:else}
        <div class="form-row">
          <label>Cron (UTC)</label>
          <input type="text" bind:value={scheduleCron} placeholder="0 5 * * *" />
          <small class="muted">Example: <code>0 5 * * *</code> = 05:00 UTC daily</small>
        </div>
      {/if}

      {#if scheduleError}
        <div class="form-row">
          <div class="muted" style="color:#ffb4b4;">{scheduleError}</div>
        </div>
      {/if}
    </div>

    <div class="modal-actions">
      <button class="btn" on:click={() => showPipelineScheduleModal = false}>Cancel</button>
      <button class="btn primary" on:click={createPipelineSchedule} disabled={scheduleSubmitting}>
        {scheduleSubmitting ? 'Scheduling…' : 'Create schedule'}
      </button>
    </div>
  </div>
{/if}

  <!-- Save Workflow Modal -->
  {#if showSaveModal}
    <div class="modal-backdrop" on:click={() => showSaveModal = false}></div>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-head">
        <h3>Save Workflow</h3>
      </div>
      
      <div class="form-grid">
        <div class="form-row">
          <label>Workflow Name</label>
          <input type="text" bind:value={saveWorkflowName} placeholder="My Awesome Workflow" />
        </div>
        <div class="form-row">
          <label>Description (Optional)</label>
          <textarea rows="3" bind:value={saveWorkflowDescription} placeholder="Describe what this workflow does..."></textarea>
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn" on:click={() => showSaveModal = false}>Cancel</button>
        <button class="btn primary" on:click={saveCurrentWorkflow}>Save Workflow</button>
      </div>
    </div>
  {/if}

  <!-- Load Workflow Modal -->
  {#if showLoadModal}
    <div class="modal-backdrop" on:click={() => showLoadModal = false}></div>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-head">
        <h3>Load Workflow</h3>
      </div>
      
      <div class="workflow-list">
        {#if savedWorkflows.length === 0}
          <div class="muted">No saved workflows found</div>
        {:else}
          {#each savedWorkflows as workflow}
            <div class="workflow-item">
              <div class="workflow-info">
                <div class="workflow-name">{workflow.name}</div>
                <div class="workflow-desc muted small">{workflow.description || 'No description'}</div>
                <div class="workflow-date muted small">{new Date(workflow.created_at).toLocaleString()}</div>
              </div>
              <div class="workflow-actions">
                <button class="btn small" on:click={() => loadWorkflow(workflow.name)}>Load</button>
                <button class="btn small" on:click={() => deleteWorkflow(workflow.name)} style="color: #ff6b6b;">Delete</button>
              </div>
            </div>
          {/each}
        {/if}
      </div>
      
      <div class="modal-actions">
        <button class="btn" on:click={() => showLoadModal = false}>Close</button>
      </div>
    </div>
  {/if}

  <!-- AI Chat Modal -->
  {#if showAIChat}
    <div class="modal-backdrop" on:click={() => showAIChat = false}></div>
    <div class="modal ai-modal" on:click|stopPropagation>
      <div class="modal-head">
        <h3>🤖 OLLAMA AI Assistant</h3>
        <div class="ollama-status">
          Status: <span class={ollamaStatus.ok ? 'status-ok' : 'status-error'}>
            {ollamaStatus.status}
          </span>
        </div>
      </div>
      
      <div class="ai-chat-body">
        <div class="form-row">
          <label>Describe the workflow you want to create:</label>
          <textarea 
            rows="4" 
            bind:value={aiChatPrompt} 
            placeholder="Example: Create a workflow to process Landsat imagery, calculate NDVI, and export the results as a GeoTIFF file"
            disabled={aiGenerating}
          ></textarea>
        </div>
        
        {#if aiChatResponse}
          <div class="ai-response">
            <h4>AI Response:</h4>
            <pre>{aiChatResponse}</pre>
          </div>
        {/if}
        
        {#if !ollamaStatus.ok}
          <div class="ollama-help">
            <h4>⚠️ OLLAMA Not Available</h4>
            <p>To use the AI assistant, you need to:</p>
            <ol>
              <li>Install OLLAMA from <a href="https://ollama.ai" target="_blank">ollama.ai</a></li>
              <li>Run: <code>ollama pull llama3.2:latest</code></li>
              <li>Start OLLAMA server: <code>ollama serve</code></li>
            </ol>
          </div>
        {/if}
      </div>
      
      <div class="modal-actions">
        <button class="btn" on:click={() => showAIChat = false}>Close</button>
        <button class="btn" on:click={checkOllamaStatus}>Check Status</button>
        <button 
          class="btn primary" 
          on:click={generateWithAI} 
          disabled={aiGenerating || !ollamaStatus.ok || !aiChatPrompt.trim()}
        >
          {aiGenerating ? 'Generating...' : 'Generate Workflow'}
        </button>
      </div>
    </div>
  {/if}

  <!-- Logs Drawer -->
  <div class="logs-drawer" data-open={showLogs ? 'true' : 'false'}>
    <div class="logs-header">
      <div class="logs-title">
        <svg viewBox="0 0 24 24" width="16" height="16"><path d="M4 5h16a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V7a2 2 0 012-2zm2 4l3 3-3 3m5 0h5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>Pipeline Logs</span>
      </div>
      <div class="logs-actions">
        <button class="icon-btn" title="Copy all" on:click={() => navigator.clipboard.writeText(
          logs.map(L => `[${L.nodeId}] ${L.ok ? 'OK' : 'ERR'} ${L.text}`).join('\n')
        )}>
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M9 9h11v11H9zM5 5h11v11" stroke="currentColor" stroke-width="2" fill="none"/></svg>
        </button>
        <button class="icon-btn" title="Clear" on:click={() => logs = []}>
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M3 6h18M9 6v12m6-12v12M5 6l1-3h12l1 3" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
        </button>
        <button class="icon-btn" title="Close" on:click={() => showLogs = false}>
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M6 6l12 12M6 18L18 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>
    <div class="logs-body">
      {#if logs.length === 0}
        <div class="muted small">No logs yet. Run the pipeline to see Python prints/stdout.</div>
      {:else}
        <ul>
          {#each logs as L, k (k)}
            <li class={L.ok ? 'ok' : 'err'}>
              <code>{L.nodeId}</code> — {L.text}
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Color Variables (harmonized with manual labeler look) */
  :root {
    --bg:#0b0e11;
    --panel:#101418;
    --muted:#6b7280;
    --text:#e5e7eb;
    --accent:#60a5fa;
    --border:#1f2937;
    --gradient-accent: linear-gradient(45deg, #60a5fa, #a78bfa);
  }

  :global(html, body, #app) { height: 100%; width: 100%; }
  :global(body) { margin: 0; background: var(--bg); color: var(--text); }

  .app-root { position: fixed; inset: 0; display: flex; flex-direction: column; width: 100vw; height: 100vh; overflow: hidden; }
  @supports (height: 100svh) { .app-root { height: 100svh; } }

    .schedule-card { display:flex; flex-direction:column; gap:8px; }
    .schedule-head { display:flex; align-items:center; justify-content:space-between; }
    .schedule-date { font-weight:600; }
    .schedule-actions { display:flex; flex-wrap:wrap; gap:6px; }
    .schedule-actions .pill-x { min-width:74px; }



  /* ======= Header (glassy topbar) ======= */
  .topbar {
    display:flex; align-items:center; justify-content:space-between;
    height:58px; padding:0 10px; border-bottom:1px solid var(--border);
    background: rgba(16,20,24,0.92); backdrop-filter: blur(6px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  }
  .left, .center, .right { display:flex; align-items:center; gap:10px; }
  .center { flex:1; justify-content:center; }
  .hint { color:#aab3bf; font-size:12px; opacity:.9; }
  .brand .title {
    font-weight:800; letter-spacing:.6px; font-size:18px;
    background: var(--gradient-accent); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  }
  .icon-btn {
    display:inline-flex; align-items:center; gap:6px; padding:6px 10px; font-size:12px; line-height:1;
    border:1px solid var(--border); border-radius:10px; background:#111827; color:#e5e7eb; cursor:pointer;
  }
  .icon-btn:hover { background:#0f172a; }
  .icon-btn:disabled { opacity:.6; cursor: default; }
  .icon-btn.primary { border-color:#3b82f6; }
  .icon-btn.ghost { background:transparent; border-color:var(--border); }


  .runone-btn {
  font-size: 12px;
  padding: 2px 6px;
  border: 1px solid #777;
  border-radius: 4px;
  background: #1b1f24;
  cursor: pointer;
  color: #e8e8e8;
}


  /* ======= Main frame: sidebar + work ======= */
  .main {
    --sidebar-w: 260px;
    display: grid; grid-template-columns: var(--sidebar-w) 1fr;
    flex: 1 1 auto; min-height: 0; width: 100%;
  }
  .main[data-collapsed="true"] { --sidebar-w: 56px; }

  .sidebar {
    background: var(--panel); border-right: 1px solid var(--border);
    padding: 10px; overflow: auto; display: flex; flex-direction: column; gap: 14px;
  }
  .sidebar[data-collapsed="true"] .txt { display: none; }
  .sidebar[data-collapsed="true"] .section-title { justify-content: center; }
  .sidebar[data-collapsed="true"] .tool { justify-content: center; padding: 8px 0; }

  .section-title { display: flex; align-items: center; gap: 8px; font-size: 12px; text-transform: uppercase; letter-spacing: .7px; color: #aab3bf; margin-bottom: 8px; }
  .tool-list { display: grid; gap: 6px; }
  .tool {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 8px; font-size: 12px;
    border: 1px solid var(--border); border-radius: 8px;
    background: #0f141b; color: #d7dde6; cursor: pointer;
  }
  .tool:hover { background:#131923; }
  .muted { color: #9aa3ad; }
  .small { font-size: 12px; }
  .edge-chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .edge-pill { display:inline-flex; align-items:center; gap:6px; padding:2px 8px; border:1px solid var(--border); border-radius:999px; font-size:12px; background: rgba(255,255,255,0.04); }
  .pill-x { border:1px solid var(--border); background:#12161c; border-radius:10px; padding:0 6px; height:18px; line-height:16px; cursor:pointer; font-size:11px; color:#e8e8e8; }
  .pending { padding:4px 8px; border:1px dashed var(--border); border-radius:8px; margin-top:8px; }

  .work { min-width: 0; min-height: 0; height: 100%; }
  .split {
    position: relative; display: grid; 
    height: 100%; min-height: 0; padding: 8px; box-sizing: border-box; align-items: stretch; overflow: hidden;
  }
  .canvas-container { min-width: 0; min-height: 0; height: 100%; overflow: hidden; }
  
  /* Drag handle for resizing */
  .drag-handle {
    background: var(--border); cursor: col-resize; position: relative;
    transition: background-color 0.2s ease;
  }
  .drag-handle:hover { background: var(--accent); }
  .drag-handle::before {
    content: '⋮⋮';
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    color: var(--muted); font-size: 14px; line-height: 1;
  }
  
  @media (max-width: 900px) {
    .main { --sidebar-w: 56px; }
    .split { grid-template-columns: 1fr !important; grid-template-rows: minmax(0, 55%) 4px minmax(0, 45%); }
    .drag-handle { cursor: row-resize; }
    .drag-handle::before { content: '⋯⋯'; }
  }

  /* Canvas viewport + map */
  .right { position: relative; display: flex; min-width: 300px; min-height: 0; height: 100%; overflow: hidden; background: #0f1216; }
  .map  { flex: 1 1 auto; width: 100%; height: 100%; min-height: 0; }

  .edges-overlay { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
  .cable { fill: none; stroke: #9ad; stroke-width: 2.25; opacity: 0.95; }
  .cable:hover { stroke-width: 2.75; }

  .node {
    position: relative; width: 100%; height: 100%;
    border-radius: 10px; background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    display:flex; align-items:center; justify-content:center;
    transition: box-shadow .15s ease, border-color .15s ease, background .15s ease;
  }
  .node[aria-selected="true"] {
    border-color: #7ad; box-shadow: 0 0 0 2px rgba(122,173,221,0.35);
    background: rgba(122,173,221,0.06);
  }
  .node-title { pointer-events: none; font-weight: 600; letter-spacing: .2px; }

  .dot {
    position: absolute; width: 10px; height: 10px; border-radius: 50%;
    border: 2px solid #9ad; background: #101418; cursor: pointer;
    opacity: 0; transition: opacity .12s ease, transform .12s ease;
  }
  .node:hover .dot { opacity: 1; }
  .dot:hover { transform: scale(1.15); }
  .dot.in  { left: -6px;  top: calc(50% - 5px); }
  .dot.out { right: -6px; top: calc(50% - 5px); box-shadow: 0 0 0 2px rgba(154,205,255,0.15); }
  .dot[aria-pressed="true"] { box-shadow: 0 0 0 3px rgba(154,205,255,0.35); }

  .node-del {
    position: absolute; top: -10px; right: -10px; width: 20px; height: 20px; border-radius: 50%;
    border: 1px solid #666; background: #1b1f24; cursor: pointer; font-size: 12px; line-height: 16px; color: #bbb;
  }
  .node-del:hover { background:#222; }

  .node-config {
    position: absolute; bottom: 6px; left: 8px; right: 8px;
    display: flex; gap: 6px; justify-content: center; align-items: center;
  }
  .node-config select, .node-config .args {
    font-size: 12px; padding: 2px 6px;
    border: 1px solid #666; border-radius: 6px; background: #1b1f24; color: #e8e8e8;
  }
  .edit-btn, .preview-btn {
    font-size: 12px; padding: 2px 6px; border: 1px solid #777; border-radius: 4px;
    background: #1b1f24; cursor: pointer; color: #e8e8e8;
  }

  /* Modal (form + JSON) */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; }
  .modal {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    background: #0f141b; border: 1px solid var(--border); border-radius: 12px; padding: 14px;
    z-index: 1001; width: 640px; max-width: 94vw; max-height: 88vh; display: flex; flex-direction: column; color: #e5e7eb;
    box-shadow: 0 10px 40px rgba(0,0,0,.5);
  }
  .modal-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
  .modal-head h3 { margin:0; font-size:16px; }
  .seg { display:inline-flex; border:1px solid var(--border); border-radius:8px; overflow:hidden; }
  .seg button { border:none; background:#111827; color:#cbd5e1; padding:6px 10px; cursor:pointer; }
  .seg button.seg-active { background:#1a2230; color:#e5e7eb; }
  .form-grid { display:grid; grid-template-columns: 1fr; gap: 10px; overflow:auto; padding: 6px 2px; }
  .form-row { display:flex; flex-direction:column; gap:6px; }
  .form-row label { font-size:12px; color:#cbd5e1; }
  .form-row input[type="text"], .form-row input[type="number"], .form-row select, .form-row textarea {
    background:#0b0f14; color:#e5e7eb; border:1px solid var(--border); border-radius:8px; padding:8px;
  }
  .form-row small { color:#9aa3ad; }
  .switch { display:inline-flex; align-items:center; gap:8px; }
  .switch input { appearance: none; width:38px; height:20px; background:#222b35; border-radius:999px; position:relative; cursor:pointer; outline:none; }
  .switch input:checked { background:#375a9e; }
  .switch input::after { content:""; position:absolute; top:2px; left:2px; width:16px; height:16px; border-radius:50%; background:#e5e7eb; transition:left .16s; }
  .switch input:checked::after { left:20px; }

  .json-area { flex:1; min-height: 340px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; background:#0b0f14; color:#e5e7eb; border:1px solid var(--border); border-radius:8px; padding:10px; }

  .modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:10px; }
  .btn { background:#111827; color:#e5e7eb; border:1px solid var(--border); border-radius:10px; padding:8px 12px; cursor:pointer; }
  .btn:hover { background:#0f172a; }
  .btn.primary { border-color:#3b82f6; }

  /* Logs Drawer */
  .logs-drawer { position: fixed; left: 0; right: 0; bottom: 0; transform: translateY(100%); transition: transform .18s ease; background: #0d1117; border-top: 1px solid var(--border); color: #dbe2ea; z-index: 1002; max-height: 45dvh; display: flex; flex-direction: column; }
  .logs-drawer[data-open="true"] { transform: translateY(0); }
  .logs-header { display:flex; align-items:center; justify-content:space-between; padding:8px 10px; background:#0f141b; }
  .logs-title { display:inline-flex; align-items:center; gap:8px; font-size:12px; text-transform:uppercase; letter-spacing:.7px; color:#aab3bf; }
  .logs-actions { display:inline-flex; gap:6px; }
  .logs-body { overflow:auto; padding:10px; font-size:13px; line-height:1.35; }
  .logs-body ul { list-style: none; padding: 0; margin: 0; }
  .logs-body li { padding: 4px 0; border-bottom: 1px dashed #222a33; }
  .logs-body li.ok { color: #d7f5dd; }
  .logs-body li.err { color: #ffd6d6; }
  .logs-body code { background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 999px; margin-right: 6px; }

  /* Workflow Management */
  .workflow-list { max-height: 400px; overflow-y: auto; padding: 8px 0; }
  .workflow-item { 
    display: flex; justify-content: space-between; align-items: center; 
    padding: 12px; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 8px;
    background: rgba(255,255,255,0.02);
  }
  .workflow-info { flex: 1; }
  .workflow-name { font-weight: 600; color: #e5e7eb; }
  .workflow-desc { margin-top: 4px; }
  .workflow-date { margin-top: 2px; }
  .workflow-actions { display: flex; gap: 8px; }
  .btn.small { padding: 4px 8px; font-size: 12px; }

  /* AI Chat Modal */
  .modal.ai-modal { width: 800px; max-height: 90vh; }
  .ai-chat-body { flex: 1; overflow-y: auto; padding: 6px 2px; }
  .ai-response { 
    margin-top: 16px; padding: 12px; 
    background: rgba(96, 165, 250, 0.1); border: 1px solid rgba(96, 165, 250, 0.3);
    border-radius: 8px;
  }
  .ai-response h4 { margin: 0 0 8px 0; color: var(--accent); }
  .ai-response pre { 
    white-space: pre-wrap; font-size: 13px; line-height: 1.4; 
    margin: 0; max-height: 300px; overflow-y: auto;
  }
  
  .ollama-status { font-size: 12px; }
  .status-ok { color: #4ade80; }
  .status-error { color: #f87171; }
  
  .ollama-help { 
    margin-top: 16px; padding: 12px; 
    background: rgba(251, 146, 60, 0.1); border: 1px solid rgba(251, 146, 60, 0.3);
    border-radius: 8px;
  }
  .ollama-help h4 { margin: 0 0 8px 0; color: #fb923c; }
  .ollama-help code { 
    background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; 
    font-family: monospace; 
  }
  .ollama-help a { color: var(--accent); }
</style>
