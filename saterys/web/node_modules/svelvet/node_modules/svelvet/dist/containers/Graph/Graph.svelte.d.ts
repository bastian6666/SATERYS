import { SvelteComponentTyped } from "svelte";
import type { Graph, CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        graph: Graph;
        width: number;
        height: number;
        minimap?: boolean | undefined;
        controls?: boolean | undefined;
        toggle?: boolean | undefined;
        fixedZoom?: boolean | undefined;
        pannable?: boolean | undefined;
        disableSelection?: boolean | undefined;
        ZOOM_INCREMENT?: number | undefined;
        PAN_INCREMENT?: number | undefined;
        PAN_TIME?: number | undefined;
        MAX_SCALE?: number | undefined;
        MIN_SCALE?: number | undefined;
        selectionColor: CSSColorString;
        backgroundExists: boolean;
        fitView?: boolean | "resize" | undefined;
        trackpadPan: boolean;
        modifier: 'alt' | 'ctrl' | 'shift' | 'meta';
        theme?: string | undefined;
        title: string;
        drawer?: boolean | undefined;
        contrast?: boolean | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
        background: {};
        minimap: {};
        drawer: {};
        controls: {};
        toggle: {};
        contrast: {};
    };
};
export type GraphProps = typeof __propDef.props;
export type GraphEvents = typeof __propDef.events;
export type GraphSlots = typeof __propDef.slots;
export default class Graph extends SvelteComponentTyped<GraphProps, GraphEvents, GraphSlots> {
}
export {};
