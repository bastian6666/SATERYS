import type { Node, Anchor } from './';
export interface SvelvetConnectionEvent {
    sourceNode: Node;
    sourceAnchor: Anchor;
    targetNode: Node;
    targetAnchor: Anchor;
}
export interface AnchorConnectionEvent {
    node: Node;
    anchor: Anchor;
    connectedNode: Node;
    connectedAnchor: Anchor;
}
