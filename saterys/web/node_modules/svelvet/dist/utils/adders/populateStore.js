export function populateStore(nodes, graph) {
    // for (const node of nodes) {
    // graph.nodes.add(node, node.id);
    graph.nodes.update((existingNodes) => {
        // Add nodes to the Map, using node.id as the key
        nodes.forEach((node) => {
            existingNodes.set(node.id, node);
        });
        return existingNodes; // Return the updated Map
    });
}
