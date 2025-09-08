import { writable } from 'svelte/store';
export function generateInput(initialData) {
    const newStore = {};
    for (const key in initialData) {
        newStore[key] = writable(initialData[key]);
    }
    return writable(newStore);
}
