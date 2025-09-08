import type { GraphDimensions } from '../../types';
export declare function calculateFitView(dimensions: GraphDimensions, bounds: {
    top: number;
    left: number;
    right: number;
    bottom: number;
}): {
    x: null;
    y: null;
    scale: null;
} | {
    x: number;
    y: number;
    scale: number;
};
