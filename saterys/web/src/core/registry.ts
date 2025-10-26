// saterys/web/src/core/registry.ts
/**
 * UI contribution registry for SATERYS plugins.
 * 
 * Plugins can register toolbar items, menu items, keyboard shortcuts, and canvas overlays.
 */

import type { AppContext } from './context';

export type Command = (ctx: AppContext) => void | Promise<void>;

export interface ToolbarItem {
  id: string;
  group: string;
  label?: string;
  icon?: any;
  run: Command;
  order?: number;
  when?: string; // Conditional display expression
}

export interface MenuItem {
  id: string;
  menu: 'layer/context' | 'app/main' | 'canvas/context';
  order?: number;
  when?: string; // Conditional display expression
  run: Command;
}

export interface Shortcut {
  combo: string;
  run: Command;
}

export interface Overlay {
  id: string;
  zIndex?: number;
  draw: (g: CanvasRenderingContext2D, view: any, ctx: AppContext) => void;
}

const _toolbar: ToolbarItem[] = [];
const _menus: MenuItem[] = [];
const _keys: Shortcut[] = [];
const _overlays: Overlay[] = [];

export function registerToolbar(item: ToolbarItem) {
  _toolbar.push(item);
}

export function registerMenu(item: MenuItem) {
  _menus.push(item);
}

export function registerShortcut(combo: string, run: Command) {
  _keys.push({ combo, run });
}

export function registerOverlay(overlay: Overlay) {
  _overlays.push(overlay);
}

export function listToolbar(): ToolbarItem[] {
  return _toolbar.slice().sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
}

export function listMenus(menu: MenuItem['menu']): MenuItem[] {
  return _menus
    .filter(m => m.menu === menu)
    .sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
}

export function listShortcuts(): Shortcut[] {
  return _keys;
}

export function listOverlays(): Overlay[] {
  return _overlays.slice().sort((a, b) => (a.zIndex ?? 0) - (b.zIndex ?? 0));
}
