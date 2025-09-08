import type { Graph } from '../../types';
export declare const calculateRelativeCursor: (e: {
    clientX: number;
    clientY: number;
}, top: number, left: number, width: number, height: number, scale: number, translation: {
    x: number;
    y: number;
}) => {
    x: number;
    y: number;
};
export declare function calculateRelativePosition(dimensions: Graph['dimensions'], transforms: Graph['transforms'], position: {
    x: number;
    y: number;
}): {
    scaled: {
        x: number;
        y: number;
    };
    scale: number;
};
