import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        output: boolean;
        input: boolean;
        connecting: boolean;
        connected: boolean;
        hovering: boolean;
        bgColor: CSSColorString | null;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type DefaultAnchorProps = typeof __propDef.props;
export type DefaultAnchorEvents = typeof __propDef.events;
export type DefaultAnchorSlots = typeof __propDef.slots;
export default class DefaultAnchor extends SvelteComponentTyped<DefaultAnchorProps, DefaultAnchorEvents, DefaultAnchorSlots> {
}
export {};
