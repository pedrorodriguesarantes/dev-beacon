<template>
  <aside class="bg-white rounded-2xl p-4 shadow flex flex-col w-65">
    <RouterLink to="/" class="self-center mb-2 hover:opacity-90 transition">
      <img src="/images/logo.png" alt="Logo" class="w-14 h-14 object-contain rounded-lg" />
    </RouterLink>

    <nav class="mt-2 flex-1 overflow-y-auto pr-1">
      <div v-for="group in computedGroups" :key="group.title" class="mt-6 first:mt-0">
        <h4 class="uppercase text-xs font-semibold text-gray-400 tracking-wider pl-2 mb-1">
          {{ group.title }}
        </h4>

        <!-- Button -->
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
          />
          <div class="flex flex-col text-left flex-1">
            <span
              :class="isActive(opt)
                ? 'text-indigo-700 font-medium'
                : 'text-gray-700 font-medium'"
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

          <!-- trash for saved dashboards -->
          <TrashIcon
            v-if="opt.id"
            class="w-5 h-8 text-gray-400 hover:text-red-500 shrink-0"
            @click.stop="deleteDashboard(opt.id)"
          />
        </button>
      </div>

      <!-- footer -->
      <a
        href="https://reshapelab.site"
        target="_blank"
        class="mt-6 flex justify-center hover:opacity-90 transition"
      >
        <img
          src="/images/labLogo.png"
          alt="Reshape Lab logo"
          class="w-full max-w-[15rem] h-auto object-contain"
        />
      </a>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { TrashIcon } from '@heroicons/vue/24/solid'
import { ref, onMounted, onUnmounted, computed } from 'vue'

/* ───────── props & router ───────── */
const props = defineProps({
  owner: { type: String, required: true },
  repo : { type: String, required: true },
})
const route  = useRoute()
const router = useRouter()

/* ───────── static groups ───────── */
const staticGroups = [
  {
    title: 'Discover',
    options: [
      {
        value      : 'custom-dashboard-builder',
        label      : 'Customize Dashboard',
        description: 'Create a new dashboard with the builder',
        path       : (o, r) => `/repos/${o}/${r}/builder`,
      },
    ],
  },
  {
    title: 'Statistics',
    options: [
      {
        value      : 'issues-dashboard',
        label      : 'Productivity (Issue)',
        description: 'Issues KPIs & trends',
        path       : (o, r) => `/repos/${o}/${r}/issues`,
      },
      {
        value      : 'pull-requests-dashboard',
        label      : 'Productivity (Pull Request)',
        description: 'Pull-request KPIs',
        path       : (o, r) => `/repos/${o}/${r}/pullRequests`,
      },
      {
        value      : 'engagement-dashboard',
        label      : 'Engagement',
        description: 'Community Engagement',
        path       : (o, r) => `/repos/${o}/${r}/engagement`,
      },
      {
        value      : 'newcomers-dashboard',
        label      : 'Newcomers',
        description: 'Newcomers reception',
        path       : (o, r) => `/repos/${o}/${r}/newcomers`,
      },
    ],
  },
  {
    title: 'Developer Analysis',
    options: [
      {
        value      : 'turnover-prediction-dashboard',
        label      : 'Turnover Prediction',
        description: 'Churn risk model',
        path       : (o, r) => `/repos/${o}/${r}/turnover-prediction`,
      },
      {
        value      : 'turnover-impact-dashboard',
        label      : 'Turnover Impact Analysis',
        description: 'How churn affects KPIs',
        path       : (o, r) => `/repos/${o}/${r}/turnover-impact`,
      },
    ],
  },
  { title: 'Our Team', options: [] },
]

/* ───────── saved dashboards ───────── */
const savedDashboards = ref([])

function loadSaved () {
  savedDashboards.value = JSON.parse(localStorage.getItem('savedDashboards') || '[]')
}

onMounted(() => {
  loadSaved()                                      // first load
  window.addEventListener('dashboards-updated', loadSaved)
})

onUnmounted(() => {
  window.removeEventListener('dashboards-updated', loadSaved)
})

/* ───────── computed groups ───────── */
const computedGroups = computed(() => {
  const savedGroup = {
    title  : 'Saved Dashboards',
    options: savedDashboards.value.map(d => ({
      value      : `saved-${d.id}`,
      label      : d.title || 'Untitled',
      description: 'Saved layout',
      id         : d.id,
      path       : `/repos/${props.owner}/${props.repo}/saved/${d.id}`,
    })),
  }
  return [staticGroups[0], savedGroup, ...staticGroups.slice(1)]
})

/* ───────── navigation helpers ───────── */
function navigate (opt) {
  const target = typeof opt.path === 'function'
    ? opt.path(props.owner, props.repo)
    : opt.path
  router.push(target)
}

function isActive (opt) {
  const target = typeof opt.path === 'function'
    ? opt.path(props.owner, props.repo)
    : opt.path
  return route.path === target
}

/* ───────── delete ───────── */
function deleteDashboard (id) {
  if (!confirm('Delete this dashboard?')) return
  savedDashboards.value = savedDashboards.value.filter(d => d.id !== id)
  localStorage.setItem('savedDashboards', JSON.stringify(savedDashboards.value))
  // trigger a refresh for any other listener (optional)
  window.dispatchEvent(new Event('dashboards-updated'))
}
</script>

<style scoped>
/* Tailwind handles visuals */
</style>