import { SvelteComponentTyped } from "svelte";
import type { NodeConfig } from '../../types';
declare const __propDef: {
    props: {
        mermaid?: string;
        mermaidConfig?: Record<string, NodeConfig>;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
};
export type FlowChartProps = typeof __propDef.props;
export type FlowChartEvents = typeof __propDef.events;
export type FlowChartSlots = typeof __propDef.slots;
export default class FlowChart extends SvelteComponentTyped<FlowChartProps, FlowChartEvents, FlowChartSlots> {
}
export {};
