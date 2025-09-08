import { writable } from 'svelte/store';
export function createEdgeStore() {
    const data = new Map();
    const subscribersOnChange = new Set();
    const { subscribe, set, update } = writable(data);
    const store = {
        subscribe,
        set,
        update,
        add: (item, key) => {
            if (typeof key !== 'string') {
                const elements = Array.from(key);
                const anchor1 = elements[0];
                const anchor2 = elements[1];
                anchor1.connected.update((anchors) => anchors.add(anchor2));
                anchor2.connected.update((anchors) => anchors.add(anchor1));
                if (store.match(...Array.from(key)).length)
                    return;
                subscribersOnChange.forEach((subscriber) => subscriber(item, 'connection'));
            }
            update((currentData) => {
                currentData.set(key, item);
                return currentData;
            });
            return;
        },
        getAll: () => {
            return Array.from(data.values());
        },
        get: (key) => {
            return data.get(key) || null;
        },
        match: (...args) => {
            return Array.from(data.keys()).filter((key) => {
                if (key === 'cursor')
                    return false;
                return args.every((arg) => {
                    if (!arg)
                        return true;
                    return key.has(arg);
                });
            });
        },
        fetch: (source, target) => {
            const match = Array.from(data.keys()).filter((key) => {
                if (key === 'cursor')
                    return false;
                return [source, target].every((arg) => {
                    if (!arg)
                        return true;
                    return key.has(arg);
                });
            })[0];
            // return matches.map((key) => data.get(key) as WritableEdge);
            return data.get(match) || null;
        },
        delete: (key) => {
            if (typeof key !== 'string') {
                const elements = Array.from(key);
                const anchor1 = elements[0];
                const anchor2 = elements[1];
                anchor1.connected.update((anchors) => {
                    anchors.delete(anchor2);
                    return anchors;
                });
                anchor2.connected.update((anchors) => {
                    anchors.delete(anchor1);
                    return anchors;
                });
            }
            let deleted = false;
            update((currentData) => {
                const edge = currentData.get(key);
                if (!edge)
                    return currentData;
                currentData.delete(key);
                deleted = true;
                if (typeof key !== 'string')
                    subscribersOnChange.forEach((subscriber) => subscriber(edge, 'disconnection'));
                return currentData;
            });
            return deleted;
        },
        onEdgeChange: (subscriber) => {
            subscribersOnChange.add(subscriber);
            // Return an unsubscribe function
            return () => subscribersOnChange.delete(subscriber);
        },
        count: () => data.size
    };
    return store;
}
