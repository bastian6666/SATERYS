export function buildArcStringKey(a, b) {
    const aX = Math.sign(a.x).toString();
    const aY = Math.sign(a.y).toString();
    const bX = Math.sign(b.x).toString();
    const bY = Math.sign(b.y).toString();
    return `${aX}${aY}${bX}${bY}`;
}
