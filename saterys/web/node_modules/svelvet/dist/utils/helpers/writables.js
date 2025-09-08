import { writable } from 'svelte/store';
export function makeObjectValuesWritable(object) {
    const writableObject = {};
    for (const key in object) {
        writableObject[key] = writable(object[key]);
    }
    return writableObject;
}
