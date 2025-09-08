import type { GraphDimensions, NodeStore, XYPair } from '../../types';
import type { Writable, Readable } from 'svelte/store';
export declare function createBoundsStore(nodes: NodeStore, dimensions: Readable<GraphDimensions>, scale: Writable<number>, translation: Writable<XYPair>): {
    graphBounds: Writable<{
        top: number;
        left: number;
        right: number;
        bottom: number;
    }>;
    nodeBounds: Writable<{
        top: number;
        left: number;
        right: number;
        bottom: number;
    }>;
};
