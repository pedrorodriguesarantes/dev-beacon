<template>
  <div class="flex gap-6">
    <!-- ──────── LEFT : SIDEBAR ──────── -->
    <MenuCard v-model="selectedPage" :groups="menuGroups" />

    <!-- ──────── RIGHT : MAIN CONTENT ──────── -->
    <div class="flex-1 space-y-6">
      <!-- Repository header -->
      <div
        v-if="projectInfo"
        class="flex items-center gap-4 bg-white p-4 rounded-2xl shadow"
      >
        <a
          :href="projectInfo.github"
          target="_blank"
          class="flex items-center gap-4 hover:opacity-80"
        >
          <img
            :src="projectInfo.image"
            :alt="`${projectInfo.name} logo`"
            class="w-14 h-14 rounded-lg object-contain"
          />
          <h1 class="text-xl font-bold text-gray-700">
            {{ projectInfo.name }}
          </h1>
        </a>
      </div>
      <div v-else class="text-red-500 p-4">Repository not found.</div>

      <!-- Active dashboard -->
      <component
        :is="currentComponent"
        :frame="frame"
        :frameLabel="frameLabel"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

import MenuCard            from '@/components/MenuCard.vue';
import IssuesDashboard   from '@/views/IssuesDashboard.vue';
import PullRequestDashboard      from '@/views/PullRequestDashboard.vue';
/* import CommunityActivity etc. as you create them */

import reposData from '../../public/repositories.json';

/* ───────────── STATE ───────────── */
const selectedPage = ref('IssuesDashboard');
const frame        = ref('month');
const frameLabel   = computed(() => frame.value[0].toUpperCase() + frame.value.slice(1));

/* ───────────── ROUTE / REPO INFO ───────────── */
const route  = useRoute();
const owner  = route.params.owner;
const repo   = route.params.repo;

const projectInfo = computed(() => {
  return reposData.find(p => p.github.includes(`${owner}/${repo}`));
});

/* ───────────── PAGE SWITCHER ───────────── */
const currentComponent = computed(() => {
  switch (selectedPage.value) {
    case 'IssuesDashboard': return IssuesDashboard;
    case 'PullRequestDashboard':    return PullRequestDashboard;
    /* add cases for new dashboards */
    default:
      return { template: '<div class="bg-white rounded-2xl p-8 shadow text-gray-500">Coming soon…</div>' };
  }
});
</script>
