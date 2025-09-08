import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: Record<string, never>;
    events: {
        groupClick: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type GroupBoxRendererProps = typeof __propDef.props;
export type GroupBoxRendererEvents = typeof __propDef.events;
export type GroupBoxRendererSlots = typeof __propDef.slots;
export default class GroupBoxRenderer extends SvelteComponentTyped<GroupBoxRendererProps, GroupBoxRendererEvents, GroupBoxRendererSlots> {
}
export {};
