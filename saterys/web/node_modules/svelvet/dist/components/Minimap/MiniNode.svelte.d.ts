import { SvelteComponentTyped } from "svelte";
import type { CSSColorString, Node } from '../../types';
declare const __propDef: {
    props: {
        node: Node;
        hidden?: boolean;
        toggleHidden: (node: Node) => void;
        top: number;
        left: number;
        nodeColor?: CSSColorString | null;
        hideable: boolean;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type MiniNodeProps = typeof __propDef.props;
export type MiniNodeEvents = typeof __propDef.events;
export type MiniNodeSlots = typeof __propDef.slots;
export default class MiniNode extends SvelteComponentTyped<MiniNodeProps, MiniNodeEvents, MiniNodeSlots> {
}
export {};
