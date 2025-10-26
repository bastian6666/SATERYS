// saterys/web/src/core/context.ts
/**
 * AppContext provides a unified interface for plugins to access core application services.
 */
let _ctx;
export function setContext(c) {
    _ctx = c;
}
export function getContext() {
    return _ctx;
}
