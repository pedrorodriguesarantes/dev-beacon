<template>
    <!-- Same layout as the LineCard but embeds a bar chart instead -->
    <div class="bg-white rounded-2xl p-4 shadow flex flex-col gap-4 h-full">
      <!-- metric label + value -->
      <div>
        <span class="block text-xs font-medium text-gray-500 tracking-wide">
          {{ title }}
        </span>
        <span class="text-2xl font-semibold leading-tight">
          {{ formattedValue }}
        </span>
      </div>
  
      <!-- mini bar chart -->
      <BarChart :series="series" :height="height" />
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import BarChart      from './BarChart.vue';
  
  const props = defineProps({
    title:  { type: String,           required: true },
    value:  { type: [Number, String], required: true },
    series: { type: Array,            default: () => [] },
    height: { type: String,           default: '200px' }
  });
  
  const formattedValue = computed(() =>
    typeof props.value === 'number' ? props.value.toLocaleString() : props.value
  );
  </script>
  
  <style scoped>
  /* Tailwind handles visuals */
  </style>