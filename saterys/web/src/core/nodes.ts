// saterys/web/src/core/nodes.ts
/**
 * Node-graph plugin system for custom processing nodes.
 */

import type { AppContext } from './context';

export type NodeIO = {
  id: string;
  kind: 'raster' | 'vector' | 'number' | 'string' | string;
  default?: any;
};

export type NodeType = {
  type: string;
  label: string;
  inputs: NodeIO[];
  outputs: NodeIO[];
  run: (ctx: AppContext, inputs: Record<string, any>) => Promise<Record<string, any>>;
  serialize?: (node: any) => any;
  deserialize?: (node: any, data: any) => void;
};

const _nodes = new Map<string, NodeType>();

export function registerNodeType(nodeType: NodeType) {
  _nodes.set(nodeType.type, nodeType);
}

export function getNodeType(type: string): NodeType | undefined {
  return _nodes.get(type);
}

export function listNodeTypes(): NodeType[] {
  return [..._nodes.values()];
}
