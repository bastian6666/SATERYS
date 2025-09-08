import { SvelteComponentTyped } from "svelte";
import type { CustomWritable } from '../../../types';
import type { CSSColorString } from '../../../types';
declare const __propDef: {
    props: {
        /**
             * @default 60
             * @description Minimum angle allowed when interacting with the knob rotation.
             */ minDegree?: number | undefined;
        /**
             * @default 300
             * @description Maximum angle allowed when interacting with the knob rotation.
             */ maxDegree?: number | undefined;
        /**
             * @default 'No default value'
             * @description This is the store that contains the output value of the knob.
             * The initial value should be passed as a property when creating the component.
             */ parameterStore: CustomWritable<number>;
        /**
             * @default 0
             * @description Minimum allowable output value of parameterStore.
             */ min?: number | undefined;
        /**
             * @default 100
             * @description Maximum allowable output value of parameterStore.
             */ max?: number | undefined;
        /**
             * @default 0
             * @description Recommendation to set step to a value that is a factor of the set the range (max - min).
             */ step?: number | undefined;
        /**
             * @default 'Value'
             * @description Label for the knob compoent.
             */ label?: string | undefined;
        /**
             * @default 0
             * @description Precision in decimal places for the output value.
             */ fixed?: number | undefined;
        /**
             * @default null
             * @description Text color.
             */ fontColor?: CSSColorString | null | undefined;
        /**
             * @default 'lightblue'
             * @description Knob background color.
             */ knobColor?: CSSColorString | null | undefined;
        /**
             * @default 'white'
             * @description Color for the output value displayed at the center of the knob.
             */ knobValueColor?: CSSColorString | null | undefined;
        /**
             * @default '#666565'
             * @description Color for indicator symbol displaying the current rotational position of the knob.
             */ indicatorColor?: CSSColorString | null | undefined;
        clamp?: ((num: number) => number) | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type KnobProps = typeof __propDef.props;
export type KnobEvents = typeof __propDef.events;
export type KnobSlots = typeof __propDef.slots;
export default class Knob extends SvelteComponentTyped<KnobProps, KnobEvents, KnobSlots> {
    get clamp(): (num: number) => number;
}
export {};
