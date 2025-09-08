import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: {
        width?: number;
        icon: "light_mode" | "dark_mode" | "arrow_left" | "arrow_right" | "filter_center_focus" | "lock" | "lock_open" | "north_west" | "south_east" | "zoom_in" | "zoom_out" | "visibility_off";
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type IconProps = typeof __propDef.props;
export type IconEvents = typeof __propDef.events;
export type IconSlots = typeof __propDef.slots;
export default class Icon extends SvelteComponentTyped<IconProps, IconEvents, IconSlots> {
}
export {};
