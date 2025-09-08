import { SvelteComponentTyped } from "svelte";
import type { Node, Graph } from '../../types';
declare const __propDef: {
    props: {
        node: Node;
        isDefault: boolean;
        useDefaults: boolean;
        center: boolean;
        nodeStore: Graph['nodes'];
        locked: Graph['locked'];
        groups: Graph['groups'];
        maxZIndex: Graph['maxZIndex'];
        centerPoint: Graph['center'];
        cursor: Graph['cursor'];
        initialNodePositions: Graph['initialNodePositions'];
        activeGroup: Graph['activeGroup'];
        editing: Graph['editing'];
        dimensionsProvided?: boolean | undefined;
        title: string;
    };
    events: {
        contextmenu: MouseEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {
            grabHandle: (node: HTMLElement) => {
                destroy(): void;
            };
            selected: boolean;
            destroy: () => void;
        };
        anchorWest: {};
        anchorEast: {};
        anchorNorth: {};
        anchorSouth: {};
    };
};
export type InternalNodeProps = typeof __propDef.props;
export type InternalNodeEvents = typeof __propDef.events;
export type InternalNodeSlots = typeof __propDef.slots;
export default class InternalNode extends SvelteComponentTyped<InternalNodeProps, InternalNodeEvents, InternalNodeSlots> {
}
export {};
