import { SvelteComponentTyped } from "svelte";
import type { WritableEdge } from '../../types';
declare const __propDef: {
    props: {
        edge: WritableEdge;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
};
export type EdgeContextProps = typeof __propDef.props;
export type EdgeContextEvents = typeof __propDef.events;
export type EdgeContextSlots = typeof __propDef.slots;
export default class EdgeContext extends SvelteComponentTyped<EdgeContextProps, EdgeContextEvents, EdgeContextSlots> {
}
export {};
