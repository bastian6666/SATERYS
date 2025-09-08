import type { Writable } from 'svelte/store';
import type { WrappedWritable } from '../../types';
import type { CSSColorString } from '../../types';
export declare function generateOutput<T extends Record<string, number | string | object | boolean | CSSColorString>, R extends number | string | object | boolean | CSSColorString>(inputs: Writable<WrappedWritable<T>>, processor: (inputs: T) => R): {
    subscribe: (this: void, run: import("svelte/store").Subscriber<R>, invalidate?: import("svelte/store").Invalidator<R> | undefined) => import("svelte/store").Unsubscriber;
    unsubscribe: () => void;
    set: null;
    update: null;
};
