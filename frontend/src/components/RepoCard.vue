<template>
  <article
    v-if="repo"
    class="flex gap-4 p-4 bg-white rounded-2xl shadow hover:shadow-md transition"
  >
    <!-- thumbnail with fallback -->
    <img
      :src="repo.image || fallbackImage"
      :alt="repo.name + ' logo'"
      @error="handleImgError"
      class="w-14 h-14 rounded-lg object-cover"
    />

    <!-- content -->
    <div class="flex-1 space-y-2">
      <header class="flex justify-between items-start">
        <h3 class="text-lg font-semibold">{{ repo.name }}</h3>
        <span v-if="repo.price" class="text-sm font-medium text-gray-500">
          {{ repo.price }}
        </span>
      </header>

      <p class="text-sm text-gray-600 line-clamp-3">
        {{ repo.description || 'No description provided.' }}
      </p>

      <!-- label badges -->
      <div class="flex flex-wrap gap-2 pt-1">
        <LabelPill
          v-for="(lbl, i) in repo.labels || []"
          :key="i"
          :text="lbl.text"
          :icon="lbl.icon"
          :color="lbl.color"
        />
      </div>

      <!-- action buttons -->
      <div class="flex gap-3 pt-1">
        <a :href="repo.github" target="_blank" class="btn btn--ghost">
          GitHub
        </a>
        <RouterLink
          :to="{
            name: 'issues',
            params: { owner: extractedOwner, repo: extractedRepo }
          }"
          class="btn btn--primary"
        >
          Metrics
        </RouterLink>
      </div>
    </div>
  </article>

  <div v-else class="text-red-500 p-4">
    Invalid repository data
  </div>
</template>

<script setup>
import { computed } from 'vue';
import LabelPill from './LabelPill.vue';

const props = defineProps(['repo']);

// Fallback image URL (replace with your actual fallback)
const fallbackImage = 'https://via.placeholder.com/150';

// Handle broken image link
function handleImgError(event) {
  event.target.src = fallbackImage;
}

// Extract owner and repo from GitHub URL
const extractedOwner = computed(() => {
  if (props.repo?.github) {
    const parts = props.repo.github.replace('https://github.com/', '').split('/');
    return parts[0] || '';
  }
  return '';
});

const extractedRepo = computed(() => {
  if (props.repo?.github) {
    const parts = props.repo.github.replace('https://github.com/', '').split('/');
    return parts[1] || '';
  }
  return '';
});
</script>

<style scoped>
.btn {
  @apply text-sm px-3 py-1.5 rounded-lg border font-medium transition;
}
.btn--ghost {
  @apply border-gray-300 text-gray-700 hover:bg-gray-50;
}
.btn--primary {
  @apply bg-indigo-600 text-white hover:bg-indigo-700;
}
</style>
