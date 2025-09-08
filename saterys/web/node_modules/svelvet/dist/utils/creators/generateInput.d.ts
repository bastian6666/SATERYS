import type { Writable } from 'svelte/store';
import type { WrappedWritable } from '../../types';
export declare function generateInput<T extends Record<string, number | string | boolean | object>>(initialData: T): Writable<WrappedWritable<T>>;
