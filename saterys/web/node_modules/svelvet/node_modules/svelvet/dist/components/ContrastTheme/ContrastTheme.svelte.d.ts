import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        contrastThemes?: string[] | undefined;
        corner?: string | undefined;
        bgColor?: CSSColorString | null | undefined;
        textColor?: CSSColorString | null | undefined;
        nodeColor?: CSSColorString | null | undefined;
        edgeColor?: CSSColorString | null | undefined;
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
