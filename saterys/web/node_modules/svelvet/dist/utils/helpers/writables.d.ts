import type { Writable } from 'svelte/store';
export declare function makeObjectValuesWritable<T extends Record<string, unknown>>(object: T): {
    [K in keyof T]: Writable<T[K]>;
};
