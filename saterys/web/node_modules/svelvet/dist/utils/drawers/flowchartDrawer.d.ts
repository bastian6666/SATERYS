import type { FlowChart } from '../../types/parser';
type LayerNode = {
    id: string;
    children: Array<string>;
    parents: Array<string>;
    layer: number;
    label?: string;
    type?: string;
    propsId?: string;
    ignore?: boolean;
};
export declare function flowChartDrawer(flowChart: FlowChart): LayerNode[][];
export {};
