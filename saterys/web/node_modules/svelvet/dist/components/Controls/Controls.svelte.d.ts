import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        increment?: number;
        horizontal?: boolean;
        bgColor?: CSSColorString | null;
        iconColor?: CSSColorString | null;
        corner?: string;
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
