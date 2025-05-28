<template>
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

    <!-- mini trend chart -->
    <LineChart :series="series" :height="height" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import LineChart     from './LineChart.vue';

const props = defineProps({
  title:  { type: String,           required: true },
  value:  { type: [Number, String], required: true },
  series: { type: Array,            default: () => [] },
  height: { type: String,           default: '100px' }
});

const formattedValue = computed(() =>
  typeof props.value === 'number' ? props.value.toLocaleString() : props.value
);
</script>
