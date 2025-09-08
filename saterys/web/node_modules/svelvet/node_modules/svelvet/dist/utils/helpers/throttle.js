export function throttle(func, limit) {
    let lastCall = 0;
    return (...args) => {
        const now = new Date().getTime();
        if (now - lastCall >= limit) {
            lastCall = now;
            func(...args);
        }
    };
}
