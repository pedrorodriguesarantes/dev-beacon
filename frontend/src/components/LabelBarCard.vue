<template>
    <div class="bg-white rounded-2xl p-4 shadow flex flex-col gap-4">
      <span class="text-sm text-gray-500">Issues Opened By Label</span>
      <v-chart :option="option" class="w-full h-28" />
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { use } from 'echarts/core';
  import VChart from 'vue-echarts';
  import { BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  
  use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);
  
  const props = defineProps({ data: Array });
  const option = computed(() => ({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 0, right: 0, top: 0, bottom: 0, containLabel: true },
    xAxis: { type: 'value', splitLine: { show: false } },
    yAxis: { type: 'category', data: props.data.map(d => d.label), axisTick: { show: false } },
    series: [{ type: 'bar', data: props.data.map(d => d.count), barWidth: '60%', smooth: true }]
  }));
  </script>