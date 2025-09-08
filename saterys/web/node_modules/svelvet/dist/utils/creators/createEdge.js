import { writable } from 'svelte/store';
import * as s from '../../constants/styles';
import { sortEdgeKey } from '../helpers/sortKey';
export function createEdge(connection, component, config) {
    const { source, target } = connection;
    const edgeId = source.id && target.id ? sortEdgeKey(source.id, target.id) : 'cursor';
    const writableEdge = {
        id: edgeId,
        target: connection.target,
        source: connection.source,
        component,
        type: writable(config?.type || null),
        color: config?.color || writable(null),
        width: writable(config?.width || 0),
        animated: writable(config?.animated || false),
        rendered: writable(false),
        start: config?.start || null,
        end: config?.end || null
    };
    // if (config?.raiseEdges) writableEdge.raiseEdgeOnSelect = true;
    // if (config?.edgesAbove) writableEdge.edgesAbove = true;
    if (config?.disconnect)
        writableEdge.disconnect = true;
    if (config?.label) {
        const baseLabel = {
            text: writable(config?.label.text),
            color: writable(config?.label?.color || s.EDGE_LABEL_COLOR),
            textColor: writable(config?.label?.textColor || s.EDGE_LABEL_TEXT_COLOR),
            fontSize: writable(config?.label?.fontSize || s.EDGE_LABEL_FONT_SIZE),
            dimensions: {
                width: writable(config?.label.dimensions?.width || s.EDGE_LABEL_WIDTH),
                height: writable(config?.label.dimensions?.height || s.EDGE_LABEL_HEIGHT)
            },
            borderRadius: writable(config?.label.borderRadius || s.EDGE_LABEL_BORDER_RADIUS)
        };
        writableEdge.label = baseLabel;
    }
    return writableEdge;
}
