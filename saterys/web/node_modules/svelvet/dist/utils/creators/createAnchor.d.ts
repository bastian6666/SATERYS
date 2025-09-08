import type { Anchor, Node, Direction, AnchorKey, Graph } from '../../types';
import type { Writable, Readable } from 'svelte/store';
import type { CustomWritable, CSSColorString, XYPair } from '../../types';
import type { ComponentType } from 'svelte';
export declare function createAnchor(graph: Graph, node: Node, id: AnchorKey, position: XYPair, dimensions: {
    width: number;
    height: number;
}, store: Anchor['store'], edge: ComponentType | null, type: 'input' | 'output' | null, direction?: Direction, dynamic?: boolean, key?: string | number | null, edgeColor?: Writable<CSSColorString | null> | CustomWritable<CSSColorString> | Readable<CSSColorString>): Anchor;
