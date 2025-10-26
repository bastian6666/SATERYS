// saterys/web/src/core/context.ts
/**
 * AppContext provides a unified interface for plugins to access core application services.
 */

export interface Commands {
  execute(cmd: {
    label: string;
    do: () => void | Promise<void>;
    undo?: () => void | Promise<void>;
  }): Promise<void>;
  invoke?(id: string): Promise<void>;
}

export interface Jobs {
  run(
    label: string,
    task: (report: (progress: number) => void) => Promise<void>
  ): Promise<void>;
}

export interface Layers {
  addFromId(id: string): void;
  remove(id: string): void;
  getSelected(): any[];
  firstRaster?: () => { id: string } | null;
}

export interface Api {
  fetch(path: string, init?: RequestInit): Promise<Response>;
}

export interface Toast {
  info(message: string): void;
  success(message: string): void;
  error(message: string): void;
}

export interface Entitlements {
  has(flag: string): boolean;
}

export interface AppContext {
  api: Api;
  jobs: Jobs;
  commands: Commands;
  layers: Layers;
  selection: {
    firstRaster?: () => { id: string } | null;
  };
  toast: Toast;
  entitlements: Entitlements;
  theme: any;
}

let _ctx: AppContext;

export function setContext(c: AppContext) {
  _ctx = c;
}

export function getContext(): AppContext {
  return _ctx;
}
