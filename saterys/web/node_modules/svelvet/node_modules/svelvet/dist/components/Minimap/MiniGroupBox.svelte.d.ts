import { SvelteComponentTyped } from "svelte";
import type { CSSColorString, Dimensions, XYPair } from '../../types';
import type { Writable } from 'svelte/store';
declare const __propDef: {
    props: {
        dimensions: Dimensions;
        position: Writable<XYPair>;
        color: Writable<CSSColorString>;
        groupName: string;
        top: number;
        left: number;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type MiniGroupBoxProps = typeof __propDef.props;
export type MiniGroupBoxEvents = typeof __propDef.events;
export type MiniGroupBoxSlots = typeof __propDef.slots;
export default class MiniGroupBox extends SvelteComponentTyped<MiniGroupBoxProps, MiniGroupBoxEvents, MiniGroupBoxSlots> {
}
export {};
