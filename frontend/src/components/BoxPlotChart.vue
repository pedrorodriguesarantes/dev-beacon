<!-- BoxPlotChart.vue -->
<template>
  <!-- autoresize lets Vue‑ECharts wait and re‑measure once Tailwind lays out the div -->
  <v-chart :option="option" class="w-full h-56" autoresize />
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import VChart from 'vue-echarts';
import { BoxplotChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

use([BoxplotChart, GridComponent, TooltipComponent, CanvasRenderer]);

// series must be an array of [min, Q1, median, Q3, max]
const props = defineProps({ series: { type: Array, default: () => [] } });

const option = computed(() => ({
  tooltip: { trigger: 'item' },
  grid:    { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis:   {
    type: 'category',
    data: props.series.map((_, i) => i + 1),
    axisTick: { show: false }
  },
  yAxis:   { type: 'value' },
  series:  [{ type: 'boxplot', data: props.series }]
}));
</script>
