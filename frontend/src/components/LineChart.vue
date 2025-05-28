<template>
    <v-chart :option="option" class="w-full h-56" autoresize />
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { use } from 'echarts/core';
  import VChart from 'vue-echarts';
  import { LineChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  
  use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);
  
  const props = defineProps({ series: Array, height: { type: String, default: '240px' } });
  const option = computed(() => ({
    tooltip: { trigger: 'axis' },
    grid: { left: 0, right: 0, top: 10, bottom: 0, containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: props.series.map(p => p.x) },
    yAxis: { type: 'value', splitLine: { show: false } },
    series: [{
      type: 'line',
      data: props.series.map(p => p.y),
      symbol: 'none',
      smooth: true,
      areaStyle: {}
    }]
  }));
  </script>