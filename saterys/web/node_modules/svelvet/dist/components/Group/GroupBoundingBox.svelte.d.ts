import { SvelteComponentTyped } from "svelte";
import type { CSSColorString, Dimensions, XYPair } from '../../types';
import type { Writable } from 'svelte/store';
declare const __propDef: {
    props: {
        dimensions: Dimensions;
        position: Writable<XYPair>;
        color: Writable<CSSColorString>;
        groupName: string;
    };
    events: {
        contextmenu: MouseEvent;
        groupClick: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type GroupBoundingBoxProps = typeof __propDef.props;
export type GroupBoundingBoxEvents = typeof __propDef.events;
export type GroupBoundingBoxSlots = typeof __propDef.slots;
export default class GroupBoundingBox extends SvelteComponentTyped<GroupBoundingBoxProps, GroupBoundingBoxEvents, GroupBoundingBoxSlots> {
}
export {};
