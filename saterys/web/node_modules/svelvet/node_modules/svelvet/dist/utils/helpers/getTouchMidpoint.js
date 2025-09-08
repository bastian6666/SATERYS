// Calculate the midpoint between two touches (used for pinch-zoom)
export function getTouchMidpoint(touch1, touch2) {
    const clientX = (touch1.clientX + touch2.clientX) / 2;
    const clientY = (touch1.clientY + touch2.clientY) / 2;
    return { clientX, clientY };
}
