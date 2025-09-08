import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: Record<string, never>;
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
};
export type DrawerControllerProps = typeof __propDef.props;
export type DrawerControllerEvents = typeof __propDef.events;
export type DrawerControllerSlots = typeof __propDef.slots;
export default class DrawerController extends SvelteComponentTyped<DrawerControllerProps, DrawerControllerEvents, DrawerControllerSlots> {
}
export {};
