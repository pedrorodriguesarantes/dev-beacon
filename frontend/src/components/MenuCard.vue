<!-- src/components/MenuCard.vue -->
<template>
  <aside class="bg-white rounded-2xl p-4 shadow flex flex-col w-56">
    <!-- ───────────── TOP : HOME LOGO ───────────── -->
    <RouterLink to="/" class="self-center mb-2 hover:opacity-90 transition">
      <img src="/images/logo.png" alt="Logo" class="w-14 h-14 object-contain rounded-lg" />
    </RouterLink>

    <!-- ───────────── MENU GROUPS ───────────── -->
    <nav class="mt-2 flex-1 overflow-y-auto pr-1">
      <div
        v-for="group in computedGroups"
        :key="group.title"
        class="mt-6 first:mt-0"
      >
        <h4
          class="uppercase text-xs font-semibold text-gray-400 tracking-wider pl-2 mb-1"
        >
          {{ group.title }}
        </h4>

        <!-- Single button -->
        <button
          v-for="opt in group.options"
          :key="opt.value"
          @click="navigate(opt)"
          class="group flex w-full items-start gap-3 px-2 py-2 rounded-lg"
          :class="
            isActive(opt) ? 'bg-indigo-50' : 'hover:bg-gray-100'
          "
        >
          <span
            class="h-5 w-1 rounded-full"
            :class="
              isActive(opt)
                ? 'bg-indigo-600'
                : 'group-hover:bg-gray-300'
            "
          ></span>

          <!-- label/description -->
          <div class="flex flex-col text-left flex-1">
            <span
              :class="
                isActive(opt)
                  ? 'text-indigo-700 font-medium'
                  : 'text-gray-700 font-medium'
              "
              class="truncate"
            >
              {{ opt.label }}
            </span>
            <span
              v-if="opt.description"
              class="text-[11px] text-gray-400 leading-snug truncate"
            >
              {{ opt.description }}
            </span>
          </div>

          <!-- trash only for custom dashboards -->
          <TrashIcon
            v-if="opt.customIdx !== undefined"
            class="w-4 h-4 text-gray-400 hover:text-red-500 shrink-0"
            @click.stop="deleteDashboard(opt.customIdx)"
          />
        </button>
      </div>

      <!-- Lab logo at the bottom -->
      <a
        href="https://reshapelab.site"
        target="_blank"
        class="mt-6 flex justify-center hover:opacity-90 transition"
      >
        <img
          src="/images/labLogo.png"
          alt="Reshape Lab logo"
          class="h-auto object-contain"
        />
      </a>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute, useRouter, RouterLink } from 'vue-router';
import { TrashIcon } from '@heroicons/vue/24/solid';
import { ref, onMounted, computed } from 'vue';

const props = defineProps({
  owner: { type: String, required: true },
  repo: { type: String, required: true },
});

const route = useRoute();
const router = useRouter();

/* ───────── STATIC GROUPS (everything except “My pages”) ───────── */
const staticGroups = [
  {
    title: 'Discover',
    options: [
      {
        value: 'custom-dashboard-builder',
        label: 'Customize Dashboard',
        description: 'Create a new dashboard with the builder',
        path: (o, r) => `/repos/${o}/${r}/builder`,
      },
    ],
  },
  {
    title: 'Statistics',
    options: [
      {
        value: 'issues-dashboard',
        label: 'Productivity (Issue)',
        description: 'Issues KPIs & trends',
        path: (o, r) => `/repos/${o}/${r}/issues`,
      },
      {
        value: 'pull-requests-dashboard',
        label: 'Productivity (Pull Request)',
        description: 'Pull‑request KPIs',
        path: (o, r) => `/repos/${o}/${r}/pullRequests`,
      },
      {
        value: 'engagement-dashboard',
        label: 'Engagement',
        description: 'Community Engagement',
        path: (o, r) => `/repos/${o}/${r}/engagement`,
      },
      {
        value: 'newcomers-dashboard',
        label: 'Newcomers',
        description: 'Newcomers reception',
        path: (o, r) => `/repos/${o}/${r}/newcomers`,
      },
    ],
  },
  {
    title: 'Developer Analysis',
    options: [
      {
        value: 'turnover-prediction-dashboard',
        label: 'Turnover Prediction',
        description: 'Churn risk model',
        path: (o, r) => `/repos/${o}/${r}/turnover-prediction`,
      },
      {
        value: 'turnover-impact-dashboard',
        label: 'Turnover Impact Analysis',
        description: 'How churn affects KPIs',
        path: (o, r) => `/repos/${o}/${r}/turnover-impact`,
      },
    ],
  },
  { title: 'Our Team', options: [] },
];

/* ───────── CUSTOM DASHBOARDS LOADED FROM CACHE ───────── */
const savedDashboards = ref([]);

onMounted(() => {
  savedDashboards.value = JSON.parse(
    localStorage.getItem('dashboards') || '[]'
  );
});

/* ───────── COMBINE STATIC + DYNAMIC GROUPS ───────── */
const computedGroups = computed(() => {
  const myPages = {
    title: 'My pages',
    options: savedDashboards.value.map((d, idx) => ({
      value: `custom-dashboard-${idx}`,
      label: d.name,
      description: 'Custom dashboard',
      customIdx: idx,
      path: (o, r) => `/repos/${o}/${r}/builder?dash=${idx}`,
    })),
  };
  return [staticGroups[0], myPages, ...staticGroups.slice(1)];
});

/* ───────── NAVIGATION & DELETE ───────── */
function navigate(opt) {
  router.push(opt.path(props.owner, props.repo));
}
function isActive(opt) {
  return route.name === opt.value;
}
function deleteDashboard(idx) {
  if (!confirm('Delete this dashboard?')) return;
  savedDashboards.value.splice(idx, 1);
  localStorage.setItem('dashboards', JSON.stringify(savedDashboards.value));
}
</script>

<style scoped>
/* Tailwind handles visuals */
</style>
