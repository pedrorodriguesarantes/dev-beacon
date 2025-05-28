<template>
    <div class="bg-white rounded-2xl p-4 shadow flex flex-col gap-1">
      <span class="text-sm text-gray-500">{{ title }}</span>
      <span class="text-3xl font-semibold leading-tight">{{ value.toLocaleString?.() ?? value }}</span>
      <span v-if="trend !== undefined" :class="['flex items-center gap-1 text-xs', trend > 0 ? 'text-green-500' : 'text-red-500']">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
          <path v-if="trend >= 0" d="M4 12l6 6 10-14"/><path v-else d="M20 12l-6-6-10 14"/>
        </svg>
        (Δ-1) to (Δ) {{ (trend * 100).toFixed(2) }}%
      </span>
    </div>
  </template>
  
  <script setup>
  defineProps({
    title: String,
    value: [Number, String],
    trend: Number
  });
  </script>