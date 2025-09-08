<script>import { getContext } from "svelte";
import { calculateRelativeCursor } from "../../../utils";
import { get } from "svelte/store";
import { roundNum } from "../../../utils";
const graph = getContext("graph");
const node = getContext("node");
const rotation = node.rotation;
const cursor = graph.cursor;
$:
  cursorX = $cursor.x;
$:
  cursorY = $cursor.y;
export let size = 200;
export let parameterStore;
let { pickerX, pickerY } = colorToPickerXY($parameterStore, size);
let picker;
let picking = false;
let wheel = true;
let wheelTop = 0;
let wheelLeft = 0;
const updatePosition = () => {
  if (!picker)
    return;
  const { top, left } = picker.getBoundingClientRect();
  const dimensions = get(graph.dimensions);
  const scale = get(graph.transforms.scale);
  const translation = get(graph.transforms.translation);
  const scaled = calculateRelativeCursor(
    { clientX: left, clientY: top },
    dimensions.top,
    dimensions.left,
    dimensions.width,
    dimensions.height,
    scale,
    translation
  );
  wheelTop = scaled.y;
  wheelLeft = scaled.x;
};
$:
  if (picking) {
    const offsetX = cursorX - wheelLeft;
    const offsetY = cursorY - wheelTop;
    const radius = size / 2;
    const dx = offsetX - radius;
    const dy = offsetY - radius;
    const distanceFromCenter = Math.sqrt(dx * dx + dy * dy);
    const normalizedDistance = Math.min(distanceFromCenter, radius);
    const angle = Math.atan2(dy, dx);
    const nodeRotationInRadians = $rotation * (Math.PI / 180);
    const rotatedAngle = angle - nodeRotationInRadians;
    const rotatedHue = (rotatedAngle + Math.PI) / (2 * Math.PI) * 360 % 360;
    const adjustedHue = rotatedHue >= 0 ? rotatedHue > 360 ? 360 - rotatedHue : rotatedHue : 360 + rotatedHue;
    const saturation = roundNum(normalizedDistance / radius * 100);
    const pickedColor = `hsl(${roundNum(adjustedHue)}, ${saturation}%, ${50 + (100 - saturation) / 2}%)`;
    const picker2 = colorToPickerXY(pickedColor, size);
    pickerX = picker2.pickerX;
    pickerY = picker2.pickerY;
    $parameterStore = pickedColor;
  }
function downUp(node2) {
  function onMouseDown(e) {
    e.stopPropagation();
    e.preventDefault();
    updatePosition();
    picking = true;
    window.addEventListener("mouseup", onMouseUp);
  }
  function onMouseUp() {
    picking = false;
    window.removeEventListener("mouseup", onMouseUp);
  }
  node2.addEventListener("mousedown", onMouseDown);
  return {
    destroy() {
      node2.removeEventListener("mousedown", onMouseDown);
    }
  };
}
function colorToPickerXY(color, size2) {
  const rgb = namedColorToRGB(color);
  const hsl = rgbToHsl(rgb);
  const hslRegex = /hsl\((\d+),\s*(\d+)%?,\s*(\d+)%?\)/;
  const match = hsl.match(hslRegex);
  if (!match) {
    throw new Error("Invalid HSL color string");
  }
  const hue = parseInt(match[1]);
  const saturation = parseInt(match[2]);
  const radius = size2 / 2;
  const angle = hue / 360 * 2 * Math.PI - Math.PI;
  const normalizedDistance = saturation / 100 * radius;
  const pickerX2 = radius + Math.cos(angle) * normalizedDistance;
  const pickerY2 = radius + Math.sin(angle) * normalizedDistance;
  return { pickerX: pickerX2, pickerY: pickerY2 };
}
function namedColorToRGB(colorName) {
  const tempElement = document.createElement("div");
  tempElement.style.color = colorName;
  document.body.appendChild(tempElement);
  const computedStyle = getComputedStyle(tempElement);
  const color = computedStyle.color;
  document.body.removeChild(tempElement);
  return color;
}
function rgbToHsl(rgbColor) {
  const rgbRegex = /rgb\((\d+),\s*(\d+),\s*(\d+)\)/;
  const match = rgbColor.match(rgbRegex);
  if (!match) {
    throw new Error("Invalid RGB color string");
  }
  const r = parseInt(match[1]) / 255;
  const g = parseInt(match[2]) / 255;
  const b = parseInt(match[3]) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;
  let hue;
  if (delta === 0) {
    hue = 0;
  } else if (max === r) {
    hue = 60 * ((g - b) / delta % 6);
    if (hue < 0) {
      hue += 360;
    }
  } else if (max === g) {
    hue = 60 * ((b - r) / delta + 2);
  } else {
    hue = 60 * ((r - g) / delta + 4);
  }
  hue = Math.round(hue);
  const lightness = (max + min) / 2;
  const saturation = delta === 0 ? 0 : delta / (1 - Math.abs(2 * lightness - 1));
  return `hsl(${hue}, ${Math.round(saturation * 100)}%, ${Math.round(lightness * 100)}%)`;
}
</script>

<div class="wrapper">
	<div
		class:picking
		class:wheel
		bind:this={picker}
		use:downUp
		style:width={size ? `${size}px` : '100%'}
		style:aspect-ratio={1 / 1}
	>
		<div class="cursor" style:top="{pickerY}px" style:left="{pickerX}px" />
	</div>
</div>

<style>
	.cursor {
		width: 8px;
		height: 8px;
		border: solid 1.5px rgb(255, 255, 255);
		transform: translate(-50%, -50%);
		border-radius: 50%;
		position: absolute;
	}
	.wrapper {
		position: relative;
	}
	.picking {
		cursor: none !important;
	}
	.wheel {
		background: conic-gradient(from -90deg, red, yellow, lime, cyan, blue, magenta, red);
		border-radius: 50%;
		cursor: crosshair;
		position: relative;
	}

	/* .line {
		position: relative;
		width: 200px;
		height: 30px;
		border-radius: 6px;
		background: linear-gradient(90deg, red, yellow, lime, cyan, blue, magenta, red);
	} */
</style>
