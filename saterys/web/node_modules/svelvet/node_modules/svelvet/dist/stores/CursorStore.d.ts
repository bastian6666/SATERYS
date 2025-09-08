/// <reference types="svelte" />
export declare const initialClickPosition: import("svelte/store").Writable<{
    x: number;
    y: number;
}>;
export declare const touchDistance: import("svelte/store").Writable<number>;
export declare const tracking: import("svelte/store").Writable<boolean>;
export declare const resizing: import("svelte/store").Writable<boolean>;
export declare const cursorPositionRaw: import("svelte/store").Readable<{
    x: number;
    y: number;
}>;
