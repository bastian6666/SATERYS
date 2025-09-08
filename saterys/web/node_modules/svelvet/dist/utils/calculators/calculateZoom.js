import { MIN_ZOOM, MAX_ZOOM } from '../../constants';
export function calculateZoom(scale, delta, zoomIncrement) {
    const scaleAdjustment = delta * zoomIncrement;
    const newScale = scale - scaleAdjustment;
    return Number(Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newScale)).toFixed(9));
}
