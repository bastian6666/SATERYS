import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        contrastThemes?: string[];
        corner?: string;
        bgColor?: CSSColorString | null;
        textColor?: CSSColorString | null;
        nodeColor?: CSSColorString | null;
        edgeColor?: CSSColorString | null;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type ContrastThemeProps = typeof __propDef.props;
export type ContrastThemeEvents = typeof __propDef.events;
export type ContrastThemeSlots = typeof __propDef.slots;
export default class ContrastTheme extends SvelteComponentTyped<ContrastThemeProps, ContrastThemeEvents, ContrastThemeSlots> {
}
export {};
