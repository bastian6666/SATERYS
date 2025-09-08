import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
import type { BackgroundStyles } from '../../types/general';
declare const __propDef: {
    props: {
        style?: BackgroundStyles | undefined;
        gridWidth?: number | undefined;
        dotSize?: number | undefined;
        bgColor?: CSSColorString | null | undefined;
        dotColor?: CSSColorString | null | undefined;
        opacityThreshold?: number | undefined;
        majorGrid?: number | undefined;
        /**
             * @default 0.4
             * @description The minimum opacity of the background grid
             */ minOpacity?: number | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type BackgroundProps = typeof __propDef.props;
export type BackgroundEvents = typeof __propDef.events;
export type BackgroundSlots = typeof __propDef.slots;
export default class Background extends SvelteComponentTyped<BackgroundProps, BackgroundEvents, BackgroundSlots> {
}
export {};
