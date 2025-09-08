<script context="module">import { writable } from "svelte/store";
import { addProps } from "../../utils";
import Icon from "../../assets/icons/Icon.svelte";
const leftAnchorCounter = writable(0);
const rightAnchorCounter = writable(0);
const topAnchorCounter = writable(0);
const bottomAnchorCounter = writable(0);
const selfAnchorCounter = writable(0);
let invisible;
let nodeConnect;
let input;
let output;
let multiple;
let direction;
let dynamic;
let anchorEdgeLabel;
let anchorLocked;
let anchorBgColor;
let directionValue;
let edgeProps = void 0;
let anchorsCreated = {
  self: [],
  left: [],
  right: [],
  top: [],
  bottom: []
};
export const createAnchorProps = (createAnchors, anchorPosition) => {
  if (direction == "")
    direction = void 0;
  const anchorProps = {};
  const anchorPropNames = [
    "invisible",
    "nodeConnect",
    "input",
    "output",
    "multiple",
    "direction",
    "dynamic",
    "edgeLabel",
    "locked",
    "bgColor",
    "edge"
  ];
  const anchorPropsArray = [
    invisible,
    nodeConnect,
    input,
    output,
    multiple,
    direction,
    dynamic,
    anchorEdgeLabel,
    anchorLocked,
    anchorBgColor,
    edgeProps
  ];
  addProps(anchorPropNames, anchorPropsArray, anchorProps);
  if (Object.keys(anchorProps).length) {
    if (createAnchors) {
      return {
        self: [...anchorsCreated.self],
        left: [...anchorsCreated.left],
        right: [...anchorsCreated.right],
        top: [...anchorsCreated.top],
        bottom: [...anchorsCreated.bottom]
      };
    }
    if (anchorPosition === "addLeftAnchor")
      anchorsCreated.left.push(anchorProps);
    else if (anchorPosition === "addRightAnchor")
      anchorsCreated.right.push(anchorProps);
    else if (anchorPosition === "addTopAnchor")
      anchorsCreated.top.push(anchorProps);
    else if (anchorPosition === "addBottomAnchor")
      anchorsCreated.bottom.push(anchorProps);
    else if (anchorPosition === "addSelfAnchor")
      anchorsCreated.self.push(anchorProps);
  }
  return;
};
const handleAnchorLockedButtonClick = (e) => {
  const target = e.target;
  anchorLocked = target.checked;
};
const handleInvisibleButtonClick = (e) => {
  const target = e.target;
  invisible = target.checked;
};
const handleNodeConnectButtonClick = (e) => {
  const target = e.target;
  nodeConnect = target.checked;
};
const handleInputButtonClick = (e) => {
  const target = e.target;
  input = target.checked;
};
const handleOutputButtonClick = (e) => {
  const target = e.target;
  output = target.checked;
};
const handleMultipleButtonClick = (e) => {
  const target = e.target;
  multiple = target.checked;
};
const handleDynamicButtonClick = (e) => {
  const target = e.target;
  dynamic = target.checked;
};
const handleDirectionButtonClick = (e) => {
  const target = e.target;
  if (target.value == "")
    direction = void 0;
  else {
    direction = target.value;
  }
};
const handleAnchorResetButtonClick = (e) => {
  invisible = void 0;
  nodeConnect = void 0;
  input = void 0;
  output = void 0;
  multiple = void 0;
  direction = void 0;
  dynamic = void 0;
  anchorEdgeLabel = void 0;
  anchorLocked = void 0;
  anchorBgColor = void 0;
  anchorsCreated.left = [];
  anchorsCreated.right = [];
  anchorsCreated.top = [];
  anchorsCreated.bottom = [];
  anchorsCreated.self = [];
  selfAnchorCounter.set(0);
  leftAnchorCounter.set(0);
  rightAnchorCounter.set(0);
  topAnchorCounter.set(0);
  bottomAnchorCounter.set(0);
  const formElement = e.target;
  if (e)
    formElement.reset();
};
const addAnchor = (e) => {
  const formEvent = e.target;
  const addAnchorID = formEvent?.parentElement?.id || formEvent?.id;
  createAnchorProps(false, addAnchorID);
  if (addAnchorID === "addLeftAnchor")
    leftAnchorCounter.set(anchorsCreated.left.length);
  else if (addAnchorID === "addRightAnchor")
    rightAnchorCounter.set(anchorsCreated.right.length);
  else if (addAnchorID === "addTopAnchor")
    topAnchorCounter.set(anchorsCreated.top.length);
  else if (addAnchorID === "addBottomAnchor")
    bottomAnchorCounter.set(anchorsCreated.bottom.length);
  else if (addAnchorID === "addSelfAnchor")
    selfAnchorCounter.set(anchorsCreated.self.length);
};
const deleteAnchor = (e) => {
  const formEvent = e.target;
  const deleteAnchorID = formEvent?.parentElement?.id || formEvent?.id;
  if (deleteAnchorID === "deleteLeftAnchor") {
    anchorsCreated.left.pop();
    leftAnchorCounter.set(anchorsCreated.left.length);
  } else if (deleteAnchorID === "deleteRightAnchor") {
    anchorsCreated.right.pop();
    rightAnchorCounter.set(anchorsCreated.right.length);
  } else if (deleteAnchorID === "deleteTopAnchor") {
    anchorsCreated.top.pop();
    topAnchorCounter.set(anchorsCreated.top.length);
  } else if (deleteAnchorID === "deleteBottomAnchor") {
    anchorsCreated.bottom.pop();
    bottomAnchorCounter.set(anchorsCreated.bottom.length);
  } else if (deleteAnchorID === "deleteSelfAnchor") {
    anchorsCreated.self.pop();
    selfAnchorCounter.set(anchorsCreated.self.length);
  }
};
</script>

<div id="anchorContainer">
	<!-- On submit resets all the values on the input field in the form to default -->
	<form on:submit|preventDefault={handleAnchorResetButtonClick}>
		<ul aria-labelledby="select_props">
			<li class="list-item">
				<label for="anchorBgColor">Background: </label>
				<input id="anchorBgColor" class="colorWheel" type="color" bind:value={anchorBgColor} />
			</li>
			<li class="list-item">
				<label for="invisible">Invisible: </label>
				<input
					id="invisible"
					type="checkbox"
					bind:value={invisible}
					on:change={handleInvisibleButtonClick}
				/>
			</li>
			<li class="list-item">
				<label for="nodeConnect">Node Connect: </label>
				<input
					id="nodeConnect"
					type="checkbox"
					bind:value={nodeConnect}
					on:change={handleNodeConnectButtonClick}
				/>
			</li>
			<li class="list-item">
				<label for="input">Input: </label>
				<input id="input" type="checkbox" bind:value={input} on:change={handleInputButtonClick} />
			</li>
			<li class="list-item">
				<label for="output">Output: </label>
				<input
					id="output"
					type="checkbox"
					bind:value={output}
					on:change={handleOutputButtonClick}
				/>
			</li>
			<li class="list-item">
				<label for="multiple">Multiple: </label>
				<input
					id="multiple"
					type="checkbox"
					bind:value={multiple}
					on:change={handleMultipleButtonClick}
				/>
			</li>
			<li class="list-item">
				<label for="direction">Direction: </label>
				<select
					id="direction"
					bind:this={directionValue}
					bind:value={direction}
					on:change={handleDirectionButtonClick}
				>
					<option value="">-</option>
					<option value="north">North</option>
					<option value="south">South</option>
					<option value="east">East</option>
					<option value="west">West</option>
					<option value="self">Self</option>
				</select>
			</li>
			<li class="list-item">
				<label for="dynamic">Dynamic: </label>
				<input
					id="dynamic"
					type="checkbox"
					bind:value={dynamic}
					on:change={handleDynamicButtonClick}
				/>
			</li>

			<li class="list-item">
				<label for="anchorLocked">Locked: </label>
				<input
					id="anchorLocked"
					type="checkbox"
					bind:value={anchorLocked}
					on:change={handleAnchorLockedButtonClick}
				/>
			</li>

			<li class="list-item">
				<label for="addAnchors"> Add Anchors: </label>
				<button
					id="deleteSelfAnchor"
					class="deleteAnchor"
					type="button"
					on:click|stopPropagation={deleteAnchor}
				>
					<Icon icon="arrow_left" />
				</button>
				<span class="list-item counter">{$selfAnchorCounter}</span>
				<button
					id="addSelfAnchor"
					class="addAnchor"
					type="button"
					on:click|stopPropagation={addAnchor}
				>
					<Icon icon="arrow_right" />
				</button>
			</li>
			<li class="list-item anchor-directions">
				<p>Left</p>
				<p>Right</p>
			</li>
			<li class="list-item anchor-directions">
				<button id="deleteLeftAnchor" class="deleteAnchor" type="button" on:click={deleteAnchor}>
					<Icon icon="arrow_left" />
				</button>
				<span class="list-item couter">{$leftAnchorCounter}</span>
				<button id="addLeftAnchor" class="addAnchor" type="button" on:click={addAnchor}>
					<Icon icon="arrow_right" />
				</button>
				<button id="deleteRightAnchor" class="deleteAnchor" type="button" on:click={deleteAnchor}>
					<Icon icon="arrow_left" />
				</button>
				<span class="list-item couter">{$rightAnchorCounter}</span>
				<button id="addRightAnchor" class="addAnchor" type="button" on:click={addAnchor}>
					<Icon icon="arrow_right" />
				</button>
			</li>
			<li class="list-item anchor-directions">
				<p>Top</p>
				<p>Bottom</p>
			</li>
			<li class="list-item anchor-directions">
				<button id="deleteTopAnchor" class="deleteAnchor" type="button" on:click={deleteAnchor}>
					<Icon icon="arrow_left" />
				</button>
				<span class="list-item couter">{$topAnchorCounter}</span>
				<button id="addTopAnchor" class="addAnchor" type="button" on:click={addAnchor}>
					<Icon icon="arrow_right" />
				</button>
				<button id="deleteBottomAnchor" class="deleteAnchor" type="button" on:click={deleteAnchor}>
					<Icon icon="arrow_left" />
				</button>
				<span class="list-item couter">{$bottomAnchorCounter}</span>
				<button id="addBottomAnchor" class="addAnchor" type="button" on:click={addAnchor}>
					<Icon icon="arrow_right" />
				</button>
			</li>
			<li class="list-item">
				<button class="anchorResetBtn btn" type="submit" aria-label="Reset">Reset</button>
			</li>
		</ul>
	</form>
</div>

<style>
	/* Anchor dropdown Styling */
	#anchorContainer {
		width: 100%;
		font-size: 15px;
	}
	#anchorContainer ul {
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

	.addAnchor,
	.deleteAnchor {
		border: none;
		cursor: pointer;
		border-radius: 8px;
		padding: 5px;
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

	.addAnchor:hover,
	.deleteAnchor:hover {
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

	.counter {
		display: inline-block;
		width: 15px;
		margin: 0 10px;
		font-size: 18px;
	}

	.anchorResetBtn {
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

	.anchorResetBtn:hover {
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

	.anchor-directions {
		display: flex;
		justify-content: space-around;
		margin: 0;
	}
</style>
