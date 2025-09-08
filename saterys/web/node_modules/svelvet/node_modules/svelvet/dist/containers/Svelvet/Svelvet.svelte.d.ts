import { SvelteComponentTyped } from "svelte";
import type { ComponentType } from 'svelte';
import type { EdgeStyle, EndStyle, XYPair } from '../../types';
import type { NodeConfig, CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        mermaid?: string | undefined;
        /**
             * @default light
             * @description This prop is used to interface with custom style blocks created using CSS. You can create any number of
             * themes with the following selector `:root[svelvet-theme="your-theme"]` and then pass the name of your theme
             * to this prop to apply it to the graph. Please see the docs for the CSS variables options. Svelvet reserves the "light" and "dark" themes for
             * internal use.
             */ theme?: string | undefined;
        id?: string | number | undefined;
        snapTo?: number | undefined;
        /**
             * @default 1
             * @description Sets initial zoom level of the graph. This value
             * features two way binding, so changing it will update the zoom.
             */ zoom?: number | undefined;
        TD?: boolean | undefined;
        editable?: boolean | undefined;
        locked?: boolean | undefined;
        width?: number | undefined;
        height?: number | undefined;
        minimap?: boolean | undefined;
        controls?: boolean | undefined;
        toggle?: boolean | undefined;
        drawer?: boolean | undefined;
        contrast?: boolean | undefined;
        /**
             * @default `false`
             * @description When `true`, the graph will automatically adjust translation
             * and scale to fit all nodes within the viewport. When set to `resize`, this
             * will continuously happen as the viewport changes size. This value is reactive.
             */ fitView?: boolean | "resize" | undefined;
        /**
             * @default 'lightblue'
             * @description Color of the box used to select/group nodes
             */ selectionColor?: CSSColorString | undefined;
        edgeStyle?: EdgeStyle | undefined;
        endStyles?: EndStyle[] | undefined;
        edge?: ComponentType | null | undefined;
        /**
             * @default false
             * @description Boolean controlling whether or not Shift + Click enables the selection of multiple components.
             * This feature is enabled by default.
             */ disableSelection?: boolean | undefined;
        mermaidConfig?: Record<string, NodeConfig> | undefined;
        /**
             * @default { x: 0, y: 0 }
             * @type { x: number, y: number }
             * @description The initial translation of the graph. This value
             * does not currently feature two way binding
             */ translation?: XYPair | undefined;
        trackpadPan?: boolean | undefined;
        modifier?: "alt" | "ctrl" | "shift" | "meta" | undefined;
        /**
             * @default false
             * @description When a Node is selected, this prop controls whether the
             * z-index of a connected edge should be raised.
             * Setting to `true` raises the edge regardless of
             * if the source or target is selected.
             */ raiseEdgesOnSelect?: boolean | "source" | "target" | undefined;
        /**
             * @default false
             * @description Sets whether edges should, by default,
             * be placed above or below connected Nodes. Can be set
             * to `all` to force Edges above all nodes. Otherwise,
             * true essentially turns on `raiseEdgesOnSelect`, but places the
             * edges at higher z-Index than the Node.
             */ edgesAboveNode?: boolean | "all" | undefined;
        title?: string | undefined;
        /**
             * @default false
             * @description Prevents the graph scale/zoom from changing.
             */ fixedZoom?: boolean | undefined;
        /**
             * @default true
             * @description Prevents the graph from panning on click if false
             */ pannable?: boolean | undefined;
        disconnect?: ((source: [string | number, string | number], target: [string | number, string | number]) => void) | undefined;
    };
    events: {
        edgeDrop: CustomEvent<any>;
    } & {
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
        background: {
            slot: string;
        };
        toggle: {
            slot: string;
        };
        drawer: {
            slot: string;
        };
        contrast: {
            slot: string;
        };
    };
};
export type SvelvetProps = typeof __propDef.props;
export type SvelvetEvents = typeof __propDef.events;
export type SvelvetSlots = typeof __propDef.slots;
export default class Svelvet extends SvelteComponentTyped<SvelvetProps, SvelvetEvents, SvelvetSlots> {
    get disconnect(): (source: [string | number, string | number], target: [string | number, string | number]) => void;
}
export {};
