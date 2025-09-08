import { SvelteComponentTyped } from "svelte";
import type { CustomWritable } from '../../../types';
import type { CSSColorString } from '../../../types';
declare const __propDef: {
    props: {
        parameterStore: CustomWritable<number>;
        min?: number | undefined;
        max?: number | undefined;
        step?: number | undefined;
        label?: string | undefined;
        fixed?: number | undefined;
        fontColor?: CSSColorString | null | undefined;
        barColor?: CSSColorString | null | undefined;
        bgColor?: CSSColorString | null | undefined;
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
