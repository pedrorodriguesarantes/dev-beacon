<template>
  <aside class="bg-white rounded-2xl p-4 shadow flex flex-col h-screen w-56">
    <!-- Top: Home logo -->
    <RouterLink to="/" class="self-center mb-2 hover:opacity-90 transition">
      <img src="/images/logo.png" alt="Logo" class="w-14 h-14 object-contain rounded-lg" />
    </RouterLink>

    <!-- Menu groups -->
    <nav class="mt-2 flex-1 overflow-y-auto pr-1">
      <div v-for="group in menuGroups" :key="group.title" class="mt-6 first:mt-0">
        <h4 class="uppercase text-xs font-semibold text-gray-400 tracking-wider pl-2 mb-1">
          {{ group.title }}
        </h4>
        <button
          v-for="opt in group.options"
          :key="opt.value"
          @click="navigate(opt)"
          class="group flex w-full items-start gap-3 px-2 py-2 rounded-lg"
          :class="isActive(opt) ? 'bg-indigo-50' : 'hover:bg-gray-100'"
        >
          <span
            class="h-5 w-1 rounded-full"
            :class="isActive(opt) ? 'bg-indigo-600' : 'group-hover:bg-gray-300'"
          ></span>
          <div class="flex flex-col text-left">
            <span :class="isActive(opt) ? 'text-indigo-700 font-medium' : 'text-gray-700 font-medium'">
              {{ opt.label }}
            </span>
            <span v-if="opt.description" class="text-[11px] text-gray-400 leading-snug">
              {{ opt.description }}
            </span>
          </div>
        </button>
      </div>
      <!-- Lab logo at the bottom -->
      <a href="https://reshapelab.site" target="_blank" class="mt-6 flex justify-center hover:opacity-90 transition">
        <img src="/images/labLogo.png" alt="Reshape Lab logo" class="h-auto object-contain" />
      </a>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute, useRouter, RouterLink } from 'vue-router';

const props = defineProps({
  owner: { type: String, required: true },
  repo: { type: String, required: true }
});

const route = useRoute();
const router = useRouter();

const menuGroups = [
  {
    title: 'Statistics',
    options: [
      {
        value: 'issues-dashboard',
        label: 'Productivity (Issue)',
        description: 'Issues KPIs & trends',
        path: (owner, repo) => `/repos/${owner}/${repo}/issues`
      },
      {
        value: 'pull-requests-dashboard',
        label: 'Productivity (Pull Request)',
        description: 'Pull-request KPIs',
        path: (owner, repo) => `/repos/${owner}/${repo}/pullRequests`
      },
      {
        value: 'community-activity-dashboard',
        label: 'Community Activity',
        description: 'Discussions, stars, forks',
        path: (owner, repo) => `/repos/${owner}/${repo}/community-activity`
      }
    ]
  },
  {
    title: 'Developer Analysis',
    options: [
      {
        value: 'turnover-prediction-dashboard',
        label: 'Turnover Prediction',
        description: 'Churn risk model',
        path: (owner, repo) => `/repos/${owner}/${repo}/turnover-prediction`
      },
      {
        value: 'turnover-impact-dashboard',
        label: 'Turnover Impact Analysis',
        description: 'How churn affects KPIs',
        path: (owner, repo) => `/repos/${owner}/${repo}/turnover-impact`
      }
    ]
  },
  {
    title: 'Our Team',
  }
];

function navigate(opt) {
  router.push(opt.path(props.owner, props.repo));
}
function isActive(opt) {
  return route.name === opt.value;
}
</script>
