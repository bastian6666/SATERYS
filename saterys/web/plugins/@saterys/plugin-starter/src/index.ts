// saterys/web/plugins/@saterys/plugin-starter/src/index.ts
/**
 * Starter UI plugin for SATERYS
 * 
 * Demonstrates:
 * - Registering a toolbar button
 * - Making API calls to backend plugin endpoints
 * - Showing toast notifications
 * - Registering canvas overlays
 */

import { registerToolbar, registerOverlay } from '../../../../src/core/registry';
import { getContext } from '../../../../src/core/context';

const PLUGIN_ID = 'starter';

// Register toolbar button
registerToolbar({
  id: `${PLUGIN_ID}.hello`,
  group: 'analysis',
  label: 'Hello Plugin',
  order: 100,
  when: 'false',
  async run() {
    const ctx = getContext();
    ctx.toast.info('Plugin button clicked!');
    
    // Run a job that calls the backend echo endpoint
    await ctx.jobs.run('Echo Test', async (report) => {
      report(10);
      
      try {
        const res = await ctx.api.fetch(`/plugins/${PLUGIN_ID}/echo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ msg: 'Hello from UI plugin!' })
        });
        
        report(50);
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        
        const data = await res.json();
        
        report(100);
        
        if (data.ok) {
          ctx.toast.success(`Echo OK: ${data.echo}`);
        } else {
          ctx.toast.error('Echo failed');
        }
      } catch (error: any) {
        ctx.toast.error(`Error: ${error?.message || error}`);
        throw error;
      }
    });
  }
});

// Register a canvas overlay (optional example)
registerOverlay({
  id: `${PLUGIN_ID}.overlay`,
  zIndex: 500,
  draw(g: CanvasRenderingContext2D, view: any, ctx: any) {
    // Optional: Draw something on the canvas
    // This is just a placeholder - plugins can draw guides, annotations, etc.
    // Example: g.strokeText('Plugin overlay', 10, 10);
  }
});

console.log('✓ Starter UI plugin loaded');
