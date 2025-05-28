<template>
    <span
      class="inline-flex items-center gap-1 text-xs font-medium
             rounded-full px-2.5 py-0.5 border"
      :class="borderClass"
    >
      <!-- language dot -->
      <span
        v-if="icon === 'dot'"
        class="w-2 h-2 rounded-full"
        :style="{ backgroundColor: color || '#6b7280' }"
      />
      <!-- lucide icon -->
      <component
        v-else-if="icon"
        :is="`lucide-${icon}`"
        class="w-3.5 h-3.5"
      />
      <span>{{ text }}</span>
    </span>
  </template>
  
  <script setup>
  defineProps({
    text: { type: String, required: true },
    icon: String,
    color: String,
  });
  const borderClass =
    'border-gray-300 text-gray-600 bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300';
  </script>
  