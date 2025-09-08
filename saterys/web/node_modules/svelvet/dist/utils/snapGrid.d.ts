export declare const cell: {
    width: number;
    height: number;
};
/**
 * Snaps a given position to the nearest grid cell.
 * @param x - The x-coordinate of the node
 * @param y - The y-coordinate of the node
 * @returns The new snapped (x, y) position
 */
export declare function getSnappedPosition(x: number, y: number): {
    x: number;
    y: number;
};
