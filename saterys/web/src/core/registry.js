// saterys/web/src/core/registry.ts
/**
 * UI contribution registry for SATERYS plugins.
 *
 * Plugins can register toolbar items, menu items, keyboard shortcuts, and canvas overlays.
 */
const _toolbar = [];
const _menus = [];
const _keys = [];
const _overlays = [];
export function registerToolbar(item) {
    _toolbar.push(item);
}
export function registerMenu(item) {
    _menus.push(item);
}
export function registerShortcut(combo, run) {
    _keys.push({ combo, run });
}
export function registerOverlay(overlay) {
    _overlays.push(overlay);
}
export function listToolbar() {
    return _toolbar.slice().sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
}
export function listMenus(menu) {
    return _menus
        .filter(m => m.menu === menu)
        .sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
}
export function listShortcuts() {
    return _keys;
}
export function listOverlays() {
    return _overlays.slice().sort((a, b) => (a.zIndex ?? 0) - (b.zIndex ?? 0));
}
