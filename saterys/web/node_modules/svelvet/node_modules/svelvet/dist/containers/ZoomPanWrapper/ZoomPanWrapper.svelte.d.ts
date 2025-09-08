import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: {
        isMovable: boolean;
    };
    events: {
        contextmenu: MouseEvent;
        click: MouseEvent;
        touchstart: TouchEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
};
export type ZoomPanWrapperProps = typeof __propDef.props;
export type ZoomPanWrapperEvents = typeof __propDef.events;
export type ZoomPanWrapperSlots = typeof __propDef.slots;
export default class ZoomPanWrapper extends SvelteComponentTyped<ZoomPanWrapperProps, ZoomPanWrapperEvents, ZoomPanWrapperSlots> {
}
export {};
