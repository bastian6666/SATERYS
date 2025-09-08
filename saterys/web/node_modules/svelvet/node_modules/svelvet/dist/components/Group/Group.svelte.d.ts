import { SvelteComponentTyped } from "svelte";
import type { XYPair, CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        width: number;
        height: number;
        position: XYPair;
        color?: CSSColorString | undefined;
        groupName: string | number;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
};
export type GroupProps = typeof __propDef.props;
export type GroupEvents = typeof __propDef.events;
export type GroupSlots = typeof __propDef.slots;
export default class Group extends SvelteComponentTyped<GroupProps, GroupEvents, GroupSlots> {
}
export {};
