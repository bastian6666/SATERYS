import { writable } from 'svelte/store';
export function createStore() {
    const data = new Map();
    const { subscribe, set, update } = writable(data);
    const store = {
        subscribe,
        set,
        update,
        add: (item, key) => {
            update((currentData) => {
                currentData.set(key, item);
                return currentData;
            });
            return data;
        },
        get: (key) => {
            return data.get(key) || null;
        },
        getAll: () => {
            return Array.from(data.values());
        },
        delete: (key) => {
            let deleted = false;
            update((currentData) => {
                currentData.delete(key);
                deleted = true;
                return currentData;
            });
            return deleted;
        },
        count: () => data.size
    };
    return store;
}
