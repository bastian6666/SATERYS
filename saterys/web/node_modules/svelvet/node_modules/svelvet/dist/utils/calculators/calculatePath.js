export function calculatePath(path, position) {
    const pathLength = path.getTotalLength();
    const halfLength = pathLength * position;
    return path.getPointAtLength(halfLength);
}
