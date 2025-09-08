import { derived } from 'svelte/store';
import { calculateRelativeCursor } from '../calculators';
export function createDerivedCursorStore(cursorPositionRaw, dimensions, translation, scale) {
    const cursorPosition = derived([cursorPositionRaw, dimensions, translation, scale], ([$cursorPositionRaw, $dimensions, $translation, $scale]) => {
        const e = {
            clientX: $cursorPositionRaw.x,
            clientY: $cursorPositionRaw.y
        };
        return calculateRelativeCursor(e, $dimensions.top, $dimensions.left, $dimensions.width, $dimensions.height, $scale, $translation);
    });
    return cursorPosition;
}
