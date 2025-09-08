import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: {
        selected: boolean;
    };
    events: {
        connection: CustomEvent<any>;
        disconnection: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type DefaultNodeProps = typeof __propDef.props;
export type DefaultNodeEvents = typeof __propDef.events;
export type DefaultNodeSlots = typeof __propDef.slots;
export default class DefaultNode extends SvelteComponentTyped<DefaultNodeProps, DefaultNodeEvents, DefaultNodeSlots> {
}
export {};
