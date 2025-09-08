import { calculateRelativeCursor } from './calculateRelativeCursor';
export function calculateViewportCenter(dimensions, translation, scale) {
    const { width, height, top, left } = dimensions;
    const viewportCenter = { clientX: width / 2, clientY: height / 2 };
    return calculateRelativeCursor(viewportCenter, top, left, width, height, scale, translation);
}
