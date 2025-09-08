import { SvelteComponentTyped } from "svelte";
import type { CustomWritable } from '../../../types';
import type { CSSColorString } from '../../../types';
declare const __propDef: {
    props: {
        parameterStore: CustomWritable<number>;
        min?: number;
        max?: number;
        step?: number;
        label?: string;
        fixed?: number;
        fontColor?: CSSColorString | null;
        barColor?: CSSColorString | null;
        bgColor?: CSSColorString | null;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type SliderProps = typeof __propDef.props;
export type SliderEvents = typeof __propDef.events;
export type SliderSlots = typeof __propDef.slots;
export default class Slider extends SvelteComponentTyped<SliderProps, SliderEvents, SliderSlots> {
}
export {};
