export function clickOutside(node) {
    const handleClick = (event) => {
        // if a click event occurs outside a specific element(node)
        if (!event.target || !node.contains(event.target)) {
            // dispatch a custom event named 'outclick' on the node
            node.dispatchEvent(new CustomEvent('outclick'));
        }
    };
    window.addEventListener('mousedown', handleClick, true);
    return {
        destroy() {
            window.removeEventListener('mousedown', handleClick, true);
        }
    };
}
