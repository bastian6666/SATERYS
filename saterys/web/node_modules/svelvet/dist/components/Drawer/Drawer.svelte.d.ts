import { SvelteComponentTyped } from "svelte";
import type { NodeConfig, XYPair, EdgeStyle } from '../../types';
import type { ComponentType } from 'svelte';
declare const __propDef: {
    props: {
        width?: number;
        height?: number;
        minimap?: boolean;
        translation?: XYPair;
        controls?: boolean;
        edge?: ComponentType | null;
        edgeStyle?: EdgeStyle;
        snapTo?: number;
        editable?: boolean;
        fitView?: boolean | "resize";
        locked?: boolean;
        zoom?: number;
        theme?: string;
        mermaid?: string;
        mermaidConfig?: Record<string, NodeConfig>;
        TD?: boolean;
        disableSelection?: boolean;
        raiseEdgesOnSelect?: boolean | "source" | "target";
        modifier?: "alt" | "ctrl" | "shift" | "meta";
        trackpadPan?: boolean;
        toggle?: boolean;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
        minimap: {
            slot: string;
        };
        controls: {
            slot: string;
        };
        toggle: {
            slot: string;
        };
    };
};
export type DrawerProps = typeof __propDef.props;
export type DrawerEvents = typeof __propDef.events;
export type DrawerSlots = typeof __propDef.slots;
export default class Drawer extends SvelteComponentTyped<DrawerProps, DrawerEvents, DrawerSlots> {
}
export {};
