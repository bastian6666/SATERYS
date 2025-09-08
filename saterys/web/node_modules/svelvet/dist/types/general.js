const arrowTuple = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
const arrows = new Set(arrowTuple);
export const isArrow = (key) => arrows.has(key);
