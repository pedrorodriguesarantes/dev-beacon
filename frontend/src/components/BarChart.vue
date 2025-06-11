<template>
    <!-- inherit same API as your LineChart: series = [{x, y}, ...] -->
    <v-chart :option="option" :class="`w-full`" :style="{ height }" autoresize />
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { use } from 'echarts/core';
  import VChart from 'vue-echarts';
  import { BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  
  // Register ECharts modules (only once per app, but harmless re‑register)
  use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);
  
  const props = defineProps({
    series: { type: Array, default: () => [] }, // [{ x: '2025‑05‑01', y: 3 }, ...]
    height: { type: String, default: '240px' }
  });
  
  // Build ECharts option from the same input shape
  const option = computed(() => {
    const xs = props.series.map(p => p.x);
    const ys = props.series.map(p => p.y);
  
    return {
      tooltip: { trigger: 'axis' },
      grid: { left: 0, right: 0, top: 10, bottom: 0, containLabel: true },
      xAxis: {
        type: 'category',
        data: xs,
        axisTick: { alignWithLabel: true }
      },
      yAxis: {
        type: 'value',
        splitLine: { show: false }
      },
      series: [
        {
          type: 'bar',
          data: ys,
          // Optional ‑ feel free to style bars via prop later
          itemStyle: { borderRadius: 4 }
        }
      ]
    };
  });
  </script>
  
  <style scoped>
  /* Tailwind handles sizing via wrapper; no extra styles needed */
  </style>
  