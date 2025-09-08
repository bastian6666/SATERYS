import { SvelteComponentTyped } from "svelte";
import type { AnchorDrawerConfig } from '../../types';
export declare const createAnchorProps: (createAnchors: boolean, anchorPosition?: string) => {
    [key: string]: AnchorDrawerConfig[];
} | undefined;
declare const __propDef: {
    props: Record<string, never>;
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type DrawerAnchorProps = typeof __propDef.props;
export type DrawerAnchorEvents = typeof __propDef.events;
export type DrawerAnchorSlots = typeof __propDef.slots;
export default class DrawerAnchor extends SvelteComponentTyped<DrawerAnchorProps, DrawerAnchorEvents, DrawerAnchorSlots> {
}
export {};
