import { SvelteComponentTyped } from "svelte";
import type { CustomWritable } from '../../../types';
import type { CSSColorString } from '../../../types';
declare const __propDef: {
    props: {
        parameterStore: CustomWritable<boolean>;
        color?: CSSColorString | null;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type ToggleProps = typeof __propDef.props;
export type ToggleEvents = typeof __propDef.events;
export type ToggleSlots = typeof __propDef.slots;
export default class Toggle extends SvelteComponentTyped<ToggleProps, ToggleEvents, ToggleSlots> {
}
export {};
