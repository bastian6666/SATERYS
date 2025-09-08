export declare function throttle<T extends unknown[], R>(func: (...args: T) => R, limit: number): (...args: T) => void;
