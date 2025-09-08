export function populateStore(nodes, graph) {
    for (const node of nodes) {
        graph.nodes.add(node, node.id);
    }
}
