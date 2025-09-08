import type { GraphDimensions, XYPair } from '../../types';
export declare function calculateTranslation(oldScale: number, newScale: number, currentTranslation: XYPair, pointerPosition: XYPair, dimensions: GraphDimensions): {
    x: number;
    y: number;
};
