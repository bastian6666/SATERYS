export function rotateVector(vector, angle) {
    // Convert angle from degrees to radians
    const angleInRadians = angle * (Math.PI / 180);
    // Calculate rotated vector
    const rotatedX = vector.x * Math.cos(angleInRadians) - vector.y * Math.sin(angleInRadians);
    const rotatedY = vector.x * Math.sin(angleInRadians) + vector.y * Math.cos(angleInRadians);
    // Return rotated vector as an object with x and y properties
    return { x: rotatedX, y: rotatedY };
}
