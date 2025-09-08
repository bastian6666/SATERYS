const shapeRef = {
    '(': 'round',
    '[': 'square',
    '([': 'stadium',
    '[[': 'subroutine',
    '[(': 'cylindrical',
    '((': 'circle',
    '{': 'rhombus',
    '{{': 'hexagon'
};
const edgeRef = { '-': 'straight', '~': 'bezier' };
const bracketRef = { '(': ')', '[': ']', '{': '}' };
const edgeRegex = /[-=~]*>(?:\s*\|(.+?)\|)?/g;
export const flowChartParser = (mermaid) => {
    const lines = mermaid.split('\n');
    const flowChart = { parentNodes: [], nodeList: {} };
    // parse mermaid string line by line
    for (const line of lines) {
        const { parentNodes, childNodes, edge } = parseLine(line);
        for (const parentNode of parentNodes) {
            // if a parent or child exists in our flow chart, then we add to their respective parent and child node arrays, otherwise we add their relational nodes then add to the flow chart
            if (!flowChart.nodeList[parentNode.id])
                flowChart.parentNodes.push(parentNode);
            for (const childNode of childNodes) {
                if (flowChart.nodeList[parentNode.id]) {
                    if (flowChart.nodeList[childNode.id] &&
                        flowChart.nodeList[childNode.id].children.some(({ node }) => node.id === parentNode.id)) {
                        throw new Error('Circular reference detected');
                    }
                    flowChart.nodeList[parentNode.id].children.push({
                        node: flowChart.nodeList[childNode.id] || childNode,
                        ...edge
                    });
                }
                else {
                    parentNode.children.push({
                        node: flowChart.nodeList[childNode.id] || childNode,
                        ...edge
                    });
                    flowChart.nodeList[parentNode.id] = parentNode;
                }
                if (flowChart.nodeList[childNode.id])
                    flowChart.nodeList[childNode.id].parents.push({
                        node: flowChart.nodeList[parentNode.id] || parentNode
                    });
                else {
                    childNode.parents.push({ node: flowChart.nodeList[parentNode.id] || parentNode });
                    flowChart.nodeList[childNode.id] = childNode;
                }
                // remove any of the child nodes being added as a top level parent node
                flowChart.parentNodes = flowChart.parentNodes.filter((node) => node.id !== childNode.id);
            }
        }
    }
    return flowChart;
};
const parseLine = (line) => {
    const parentNodes = [];
    const childNodes = [];
    const trimmedLine = line.trim();
    let edgeString = '';
    // regex here will match any edge type along with its content if provided. that edge is then used to split the line into parent and child nodes
    const edgeStringArray = trimmedLine.match(edgeRegex);
    if (edgeStringArray)
        edgeString = edgeStringArray[0];
    else
        throw new Error('Invalid edge');
    const [parentNodesString, childNodesString] = trimmedLine.split(edgeString);
    for (const parentNode of parentNodesString.split('&'))
        parentNodes.push(nodeParser(parentNode));
    for (const childNode of childNodesString.split('&'))
        childNodes.push(nodeParser(childNode));
    const edge = edgeParser(edgeString);
    return { parentNodes, childNodes, edge };
};
const nodeParser = (node) => {
    node = node.trim();
    const id = node[0];
    const body = node.slice(1);
    let label = '';
    let shape = '';
    const type = 'Default';
    const data = { shape: '' };
    const bracketStack = [];
    for (let i = 0; i < body.length; i++) {
        if (isOpenBracket(body[i]))
            bracketStack.push(body[i]);
        else if (bracketRef[bracketStack[bracketStack.length - 1]] === body[i]) {
            shape = shapeRef[bracketStack.join('')];
            break;
        }
        else
            label += body[i];
    }
    data.shape = shape;
    data.content = label;
    return { id, data, type, children: [], parents: [], depth: 0, nesting: 0 };
};
const edgeParser = (edge) => {
    edge = edge.trim();
    let shape = '';
    const [edgeLine, content] = edge.split('|');
    const key = edgeLine[0];
    if (key in edgeRef)
        shape = edgeRef[key];
    else
        throw new Error('Not a valid edge type');
    if (content)
        return { shape, content: content.trim(), length: Math.floor((edgeLine.trim().length - 1) / 2) };
    else
        return { shape, length: Math.floor((edgeLine.trim().length - 1) / 2) };
};
function isOpenBracket(key) {
    return key in bracketRef;
}
