import type { Writable } from 'svelte/store';
import type { Node, Graph, XYPair, GroupBox } from '../../types';
export declare function captureGroup(group: Writable<Set<Node | GroupBox>>): XYPair[];
export declare function moveNodes(graph: Graph, snapTo: number): void;
export declare function moveElement(initialPosition: XYPair, delta: XYPair, position: Writable<XYPair>): void;
export declare function moveElementWithBounds(initialPosition: XYPair, delta: XYPair, position: Writable<XYPair>, bounds: {
    left: number;
    right: number;
    top: number;
    bottom: number;
}): void;
export declare function calculateRelativeBounds(groupBox: GroupBox, nodeWidth: number, nodeHeight: number): {
    left: number;
    right: number;
    top: number;
    bottom: number;
};
