<template>
  <div class="p-8 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Repositories</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="repo in repositories" :key="repo.github" class="bg-white rounded-xl shadow p-4 flex items-center gap-4">
        <img
          :src="repo.image"
          alt="Repo Logo"
          class="w-12 h-12 object-contain rounded"
        />
        <div class="flex-1">
          <h2 class="font-semibold text-lg">{{ repo.name }}</h2>
          <p class="text-sm text-gray-500">{{ repo.description }}</p>
          <router-link
            class="inline-block mt-2 text-indigo-600 hover:underline text-sm font-medium"
            :to="{
              name: 'issues-dashboard',
              params: {
                owner: getOwner(repo.github),
                repo: getRepo(repo.github)
              }
            }"
          >
            View Dashboard →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const repositories = ref([]);

// If your JSON is in /public, use fetch:
onMounted(async () => {
  const res = await fetch('/repositories.json');
  repositories.value = await res.json();
});

// Helpers to extract owner/repo from github url
function getOwner(github) {
  const match = github.match(/github\.com\/([^/]+)\/([^/]+)/);
  return match ? match[1] : '';
}
function getRepo(github) {
  const match = github.match(/github\.com\/([^/]+)\/([^/]+)/);
  return match ? match[2] : '';
}
</script>
