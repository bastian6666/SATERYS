import { SvelteComponentTyped } from "svelte";
import type { Node, Connections, CSSColorString, EdgeStyle, EndStyle } from '../../types';
import type { Direction, CustomWritable } from '../../types';
import type { InputStore, ConnectingFrom } from '../../types';
import type { ComponentType } from 'svelte';
import type { Writable, Readable } from 'svelte/store';
export declare const connectingFrom: Writable<ConnectingFrom | null>;
export declare function changeAnchorSide(anchorElement: HTMLElement, newSide: Direction, node: Node): void;
declare const __propDef: {
    props: {
        bgColor?: CSSColorString | null | undefined;
        id?: string | number | undefined;
        input?: boolean | undefined;
        output?: boolean | undefined;
        /**
             * @default dependent on `input` and `output` props
             * @description When `true`, the Anchor will accept multiple connections. This is set to true by default
             * for output anchors or anchors that have not specified an input/output prop.
             */ multiple?: boolean | undefined;
        /**
             * @default 'false'
             * @description When `true`, the Anchor will dynamically change its direction
             * based on the relative positioning of connected Nodes
             */ dynamic?: boolean | undefined;
        edge?: ComponentType | null | undefined;
        inputsStore?: InputStore | null | undefined;
        key?: string | number | null | undefined;
        outputStore?: {
            subscribe: (this: void, run: import("svelte/store").Subscriber<string | number | boolean | object>, invalidate?: import("svelte/store").Invalidator<string | number | boolean | object> | undefined) => import("svelte/store").Unsubscriber;
            unsubscribe: () => void;
            set: null;
            update: null;
        } | null | undefined;
        connections?: Connections | undefined;
        edgeColor?: Writable<CSSColorString | null> | CustomWritable<CSSColorString> | Readable<CSSColorString> | undefined;
        edgeLabel?: string | undefined;
        /**
             * @default 'false'
             * @description When `true`, connections and disconnections are not allowed. Updates the cursor on hover.
             */ locked?: boolean | undefined;
        /**
             * @default 'false'
             * @description When `true`, mouse up events on the parent Node will trigger connections to this Anchor. If this value
             * is true for multiple Anchors, connections will be assigned in order, unless an Anchor is set to accept multiple connections.
             */ nodeConnect?: boolean | undefined;
        edgeStyle?: EdgeStyle | null | undefined;
        endStyles?: EndStyle[] | undefined;
        /**
             * @default 'false'
             * @description When `true`, the default Anchor will not be rendered. It is not necessary to set this to true
             * when passing custom Anchors as children. It likely only makes sense to use this
             * in combination with the  `nodeConnect` prop.
             */ invisible?: boolean | undefined;
        direction?: Direction | undefined;
        title?: string | undefined;
        disconnect?: ((target: [string | number, string | number]) => void) | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {
            linked: boolean;
            hovering: boolean;
            connecting: boolean;
        };
        edge: {};
    };
};
export type AnchorProps = typeof __propDef.props;
export type AnchorEvents = typeof __propDef.events;
export type AnchorSlots = typeof __propDef.slots;
export default class Anchor extends SvelteComponentTyped<AnchorProps, AnchorEvents, AnchorSlots> {
    get disconnect(): (target: [string | number, string | number]) => void;
}
export {};
