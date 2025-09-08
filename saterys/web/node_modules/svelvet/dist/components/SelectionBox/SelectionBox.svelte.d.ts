import { SvelteComponentTyped } from "svelte";
import type { CSSColorString, Graph } from '../../types';
declare const __propDef: {
    props: {
        graph: Graph;
        anchor: {
            x: number;
            y: number;
            top: number;
            left: number;
        };
        adding?: boolean;
        creating?: boolean;
        color?: CSSColorString | null;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type SelectionBoxProps = typeof __propDef.props;
export type SelectionBoxEvents = typeof __propDef.events;
export type SelectionBoxSlots = typeof __propDef.slots;
export default class SelectionBox extends SvelteComponentTyped<SelectionBoxProps, SelectionBoxEvents, SelectionBoxSlots> {
}
export {};
