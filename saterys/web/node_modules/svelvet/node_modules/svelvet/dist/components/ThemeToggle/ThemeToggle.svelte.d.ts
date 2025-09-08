import { SvelteComponentTyped } from "svelte";
import type { CSSColorString } from '../../types';
declare const __propDef: {
    props: {
        main?: string | undefined;
        alt?: string | undefined;
        /**
             * @deprecated
             * @default 'light_mode'
             * @description (Do not use. Will be deprecated in the next major release.) This prop accepts a string that corresponds to the the name of an icon from the Material Icons library.
             * @link https://fonts.google.com/icons
             */ mainIcon?: string | undefined;
        /**
             * @deprecated
             * @default 'dark_mode'
             * @description (Do not use. Will be deprecated in the next major release.) This prop accepts a string that corresponds to the the name of an icon from the Material Icons library.
             *  @link https://fonts.google.com/icons
             */ altIcon?: string | undefined;
        corner?: string | undefined;
        bgColor?: CSSColorString | null | undefined;
        iconColor?: CSSColorString | null | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type ThemeToggleProps = typeof __propDef.props;
export type ThemeToggleEvents = typeof __propDef.events;
export type ThemeToggleSlots = typeof __propDef.slots;
export default class ThemeToggle extends SvelteComponentTyped<ThemeToggleProps, ThemeToggleEvents, ThemeToggleSlots> {
}
export {};
