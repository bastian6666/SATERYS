import { SvelteComponentTyped } from "svelte";
declare const __propDef: {
    props: {
        placeholder: string;
    };
    events: {
        keydown: KeyboardEvent;
        click: MouseEvent;
        mousedown: MouseEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type TextFieldProps = typeof __propDef.props;
export type TextFieldEvents = typeof __propDef.events;
export type TextFieldSlots = typeof __propDef.slots;
export default class TextField extends SvelteComponentTyped<TextFieldProps, TextFieldEvents, TextFieldSlots> {
}
export {};
