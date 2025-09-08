<script context="module">import { addProps } from "../../utils";
let edgeWidth;
let color;
let straight;
let step;
let cornerRadius;
let animate;
let edgeLabel;
let labelColor;
let textColor;
let targetColor;
export function createEdgeProps() {
  const edgeProps = {};
  const edgePropsNames = [
    "width",
    "targetColor",
    "color",
    "straight",
    "step",
    "cornerRadius",
    "animate",
    "label",
    "labelColor",
    "textColor"
  ];
  const edgePropsArray = [
    edgeWidth,
    targetColor,
    color,
    straight,
    step,
    cornerRadius,
    animate,
    edgeLabel,
    labelColor,
    textColor
  ];
  addProps(edgePropsNames, edgePropsArray, edgeProps);
  if (Object.keys(edgeProps).length)
    return edgeProps;
  return;
}
const handleStepButtonClick = (e) => {
  const target = e.target;
  step = target.checked;
};
const handleAnimateButtonClick = (e) => {
  const target = e.target;
  animate = target.checked;
};
const handleEdgeResetButtonClick = (e) => {
  edgeWidth = void 0;
  targetColor = void 0;
  color = void 0;
  straight = void 0;
  step = void 0;
  cornerRadius = void 0;
  animate = void 0;
  edgeLabel = void 0;
  labelColor = void 0;
  textColor = void 0;
  const target = e.target;
  target.reset();
};
</script>

<div id="edgeContainer">
	<!-- On submit resets all the values on the input field in the form to default -->
	<form on:submit|preventDefault={handleEdgeResetButtonClick}>
		<ul aria-labelledby="select_props">
			<li class="list-item">
				<label for="color">Background: </label>
				<input id="color" class="colorWheel" type="color" bind:value={color} />
			</li>
			<li class="list-item">
				<label for="labelColor">Label: </label>
				<input id="labelColor" class="colorWheel" type="color" bind:value={labelColor} />
			</li>
			<li class="list-item">
				<label for="textColor">Text: </label>
				<input id="textColor" class="colorWheel" type="color" bind:value={textColor} />
			</li>
			<li class="list-item">
				<label for="animate">Animate : </label>
				<input
					id="animate"
					type="checkbox"
					bind:value={animate}
					on:change={handleAnimateButtonClick}
				/>
			</li>
			<li class="list-item">
				<label for="step">Step: </label>
				<input id="step" type="checkbox" bind:value={step} on:change={handleStepButtonClick} />
			</li>
			<li class="list-item">
				<label for="cornerRadius">Corner Radius:</label>
				<input id="cornerRadius" class="inputField" type="number" bind:value={cornerRadius} />
			</li>
			<li class="list-item">
				<label for="width">Width:</label>
				<input id="width" class="inputField" type="number" bind:value={edgeWidth} />
			</li>
			<li class="list-item">
				<label for="edgeLabel">Edge Label: </label>
				<input id="edgeLabel" type="text" bind:value={edgeLabel} />
			</li>
			<li class="list-item">
				<button class="edgeResetBtn btn" aria-label="Reset">Reset</button>
			</li>
		</ul>
	</form>
</div>

<style>
	/* Edge dropdown Styling */
	#edgeContainer {
		width: 100%;
		font-size: 15px;
	}
	#edgeContainer ul {
		margin: 0;
		padding: 0;
	}

	label {
		margin-right: 10px;
	}

	.list-item {
		display: flex;
		flex-direction: row;
		align-items: center;
		list-style: none;
		margin-bottom: 10px;
		margin-right: 3px;
	}
	.colorWheel {
		-webkit-appearance: none;
		-moz-appearance: none;
		appearance: none;
		background-color: transparent;
		border: none;
		width: 35px;
		height: 35px;
		cursor: pointer;
		border-radius: 50%;
	}

	.colorWheel::-webkit-color-swatch {
		border-radius: 40%;
	}
	.colorWheel::-moz-color-swatch {
		border-radius: 40%;
	}

	.inputField {
		width: 50px;
	}

	.btn {
		width: 120px;
		padding: 8px 20px;
		margin: auto;
		margin-top: 10px;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		font-size: 15px;
		margin-left: 70px;
	}

	.edgeResetBtn {
		color: var(
			--prop-drawer-reset-button-text-color,
			var(--drawer-reset-button-text-color, var(--default-reset-drawer-button-text-color))
		);
		background-color: var(
			--prop-drawer-reset-button-color,
			var(--drawer-reset-button-color, var(--default-drawer-reset-button-color))
		);
		box-shadow: 0 0 0 var(--final-border-width) var(--final-border-color),
			var(--default-node-shadow);
	}

	.edgeResetBtn:hover {
		color: var(
			--prop-drawer-reset-button-hover-text-color,
			var(
				--drawer-reset-button-hover-text-color,
				var(--default-drawer-reset-button-hover-text-color)
			)
		);
		background-color: var(
			--prop-drawer-reset-button-hover-color,
			var(--drawer-reset-button-hover-color, var(--default-drawer-reset-button-hover-color))
		);
	}
</style>
