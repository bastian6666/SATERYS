export function sortEdgeKey(keyOne, keyTwo) {
    // Sort the strings alphabetically
    const sortedStrings = [keyOne, keyTwo].sort();
    // Concatenate the sorted strings
    const combinedString = `${sortedStrings[0]}+${sortedStrings[1]}`;
    return combinedString;
}
