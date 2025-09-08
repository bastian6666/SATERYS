import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        increment?: number | undefined;
        horizontal?: boolean | undefined;
        bgColor?: CSSColorString | null | undefined;
        iconColor?: CSSColorString | null | undefined;
        corner?: string | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {
            zoomIn: () => void;
            zoomOut: () => void;
            fitView: () => void;
            lock: () => void;
            unhideAll: () => void;
        };
    };
};
export type ControlsProps = typeof __propDef.props;
export type ControlsEvents = typeof __propDef.events;
export type ControlsSlots = typeof __propDef.slots;
export default class Controls extends SvelteComponentTyped<ControlsProps, ControlsEvents, ControlsSlots> {
}
export {};
