import type { Readable, Writable } from 'svelte/store';
import type { Graph } from '../../types';
export declare function createDerivedCursorStore(cursorPositionRaw: Readable<{
    x: number;
    y: number;
}>, dimensions: Graph['dimensions'], translation: Graph['transforms']['translation'], scale: Writable<number>): Readable<{
    x: number;
    y: number;
}>;
