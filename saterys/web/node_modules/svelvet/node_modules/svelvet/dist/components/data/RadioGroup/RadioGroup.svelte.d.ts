import { SvelteComponentTyped } from "svelte";
import type { CustomWritable } from '../../../types';
declare const __propDef: {
    props: {
        options: Array<string>;
        parameterStore: CustomWritable<string>;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type RadioGroupProps = typeof __propDef.props;
export type RadioGroupEvents = typeof __propDef.events;
export type RadioGroupSlots = typeof __propDef.slots;
export default class RadioGroup extends SvelteComponentTyped<RadioGroupProps, RadioGroupEvents, RadioGroupSlots> {
}
export {};
