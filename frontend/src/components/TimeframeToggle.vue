<template>
  <div class="inline-flex rounded-lg bg-gray-100 p-1">
    <button
      v-for="opt in options"
      :key="opt"
      :class="[
        'px-3 py-1 text-sm font-medium rounded-md focus:outline-none transition',
        modelValue === opt ? 'bg-white shadow' : 'text-gray-600 hover:bg-white'
      ]"
      @click="$emit('update:modelValue', opt)"
    >
      {{ opt.charAt(0).toUpperCase() + opt.slice(1) }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, required: true },
  options:    { type: Array,  default: () => ['day', 'week', 'month'] }
});
defineEmits(['update:modelValue']);
</script>
