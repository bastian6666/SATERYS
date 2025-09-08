import type { Writable, Readable } from 'svelte/store';
import type { AnchorKey, CSSColorString, CustomWritable, Node, XYPair } from './';
import type { generateOutput } from '../utils';
import type { ComponentType } from 'svelte';
export interface Anchor {
    id: AnchorKey;
    position: Readable<{
        x: number;
        y: number;
    }>;
    offset: Writable<XYPair>;
    connected: Writable<Set<Anchor>>;
    dynamic: Writable<boolean>;
    edge: ComponentType | null;
    direction: Writable<Direction>;
    rotation: Readable<number>;
    recalculatePosition: () => void;
    type: InputType;
    mounted: Writable<boolean>;
    inputKey: string | number | null;
    moving: Readable<boolean>;
    edgeColor: Writable<CSSColorString | null> | CustomWritable<CSSColorString> | Readable<CSSColorString>;
    store: Writable<Record<string, Writable<unknown> | Readable<unknown>>> | ReturnType<typeof generateOutput> | null;
    node: Node;
}
export type Direction = 'north' | 'south' | 'east' | 'west' | 'self';
export type InputType = 'input' | 'output' | null;
