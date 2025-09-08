import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: {
        isMovable: boolean;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
};
export type GraphRendererProps = typeof __propDef.props;
export type GraphRendererEvents = typeof __propDef.events;
export type GraphRendererSlots = typeof __propDef.slots;
export default class GraphRenderer extends SvelteComponentTyped<GraphRendererProps, GraphRendererEvents, GraphRendererSlots> {
}
export {};
