import { writable, get } from 'svelte/store';
export function generateOutput(inputs, processor) {
    const outputStore = writable();
    const updateOutputStore = () => {
        const inputValues = get(inputs);
        const currentInputs = {};
        for (const key in inputValues) {
            currentInputs[key] = get(inputValues[key]);
        }
        outputStore.set(processor(currentInputs));
    };
    const unsubscribeFns = [];
    const subscribeToNestedStores = (store) => {
        for (const key in store) {
            store[key].subscribe(() => {
                updateOutputStore();
            });
        }
    };
    const unsubscribeInputs = inputs.subscribe((wrappedInputs) => {
        unsubscribeFns.forEach((fn) => fn());
        unsubscribeFns.length = 0;
        subscribeToNestedStores(wrappedInputs);
    });
    return {
        subscribe: outputStore.subscribe,
        unsubscribe: () => {
            unsubscribeInputs();
            unsubscribeFns.forEach((fn) => fn());
        },
        set: null,
        update: null
    };
}
