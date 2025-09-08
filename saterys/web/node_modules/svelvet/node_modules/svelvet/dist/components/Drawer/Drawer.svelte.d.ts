import { SvelteComponentTyped } from "svelte";
import type { NodeConfig, XYPair, EdgeStyle } from '../../types';
import type { ComponentType } from 'svelte';
declare const __propDef: {
    props: {
        width?: number | undefined;
        height?: number | undefined;
        minimap?: boolean | undefined;
        translation?: XYPair | undefined;
        controls?: boolean | undefined;
        edge?: ComponentType | null | undefined;
        edgeStyle?: EdgeStyle | undefined;
        snapTo?: number | undefined;
        editable?: boolean | undefined;
        fitView?: boolean | "resize" | undefined;
        locked?: boolean | undefined;
        zoom?: number | undefined;
        theme?: string | undefined;
        mermaid?: string | undefined;
        mermaidConfig?: Record<string, NodeConfig> | undefined;
        TD?: boolean | undefined;
        disableSelection?: boolean | undefined;
        raiseEdgesOnSelect?: boolean | "source" | "target" | undefined;
        modifier?: "alt" | "ctrl" | "shift" | "meta" | undefined;
        trackpadPan?: boolean | undefined;
        toggle?: boolean | undefined;
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
