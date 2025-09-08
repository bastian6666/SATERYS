import { createStore } from '../utils';
import { writable } from 'svelte/store';
export const graphStore = createStore();
export const source = writable(null);
// create new graph store, less strict type check
// export const graphStore = writable<Graph | null>(null);
