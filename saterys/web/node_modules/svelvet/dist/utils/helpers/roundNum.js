export function roundNum(number, decimalPlaces = 1) {
    const factor = Math.pow(10, decimalPlaces);
    return Math.round(number * factor) / factor;
}
