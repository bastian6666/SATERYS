import { SvelteComponentTyped } from "svelte";
import type { EdgeDrawerConfig } from '../../types';
export declare function createEdgeProps(): EdgeDrawerConfig | undefined;
declare const __propDef: {
    props: Record<string, never>;
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type DrawerEdgeProps = typeof __propDef.props;
export type DrawerEdgeEvents = typeof __propDef.events;
export type DrawerEdgeSlots = typeof __propDef.slots;
export default class DrawerEdge extends SvelteComponentTyped<DrawerEdgeProps, DrawerEdgeEvents, DrawerEdgeSlots> {
}
export {};
