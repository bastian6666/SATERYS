export function addProps(propNames, propValues, propObject) {
    for (let i = 0; i < propNames.length; i++) {
        if (propValues[i] !== undefined)
            propObject[propNames[i]] = propValues[i];
    }
}
