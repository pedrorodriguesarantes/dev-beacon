<!-- src/App.vue -->
<template>
  <!-- root wrapper keeps the dashboard full‑height and gives it a light background -->
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Issues section (you can copy‑paste this component to add more dashboards later) -->
    <RouterView />
  </div>
</template>

<style>
/* optional: global font / text styles */
body {
  @apply font-sans text-gray-800;
}
</style>
