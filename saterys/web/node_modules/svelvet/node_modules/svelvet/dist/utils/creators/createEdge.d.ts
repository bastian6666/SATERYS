import type { WritableEdge, EdgeConfig, Anchor } from '../../types';
import type { ComponentType } from 'svelte';
export declare function createEdge(connection: {
    source: Anchor;
    target: Anchor;
}, component: ComponentType | null, config?: EdgeConfig): WritableEdge;
