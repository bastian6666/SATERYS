import { SvelteComponentTyped } from "svelte";
import type { CustomWritable, CSSColorString } from '../../../types';
declare const __propDef: {
    props: {
        size?: number | undefined;
        parameterStore: CustomWritable<CSSColorString>;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type ColorWheelProps = typeof __propDef.props;
export type ColorWheelEvents = typeof __propDef.events;
export type ColorWheelSlots = typeof __propDef.slots;
export default class ColorWheel extends SvelteComponentTyped<ColorWheelProps, ColorWheelEvents, ColorWheelSlots> {
}
export {};
