import { SvelteComponentTyped } from "svelte";
import type { CSSColorString, Corner } from '../../types';
declare const __propDef: {
    props: {
        width?: number | undefined;
        height?: number | undefined;
        mapColor?: CSSColorString | null | undefined;
        nodeColor?: CSSColorString | null | undefined;
        borderColor?: CSSColorString | null | undefined;
        corner?: Corner | undefined;
        hideable?: boolean | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type MinimapProps = typeof __propDef.props;
export type MinimapEvents = typeof __propDef.events;
export type MinimapSlots = typeof __propDef.slots;
export default class Minimap extends SvelteComponentTyped<MinimapProps, MinimapEvents, MinimapSlots> {
}
export {};
