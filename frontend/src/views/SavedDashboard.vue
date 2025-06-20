<!-- SavedDashboard.vue -->
<template>
    <div class="flex gap-6">
      <!-- ─────── MENU (LEFT) ─────── -->
      <MenuCard :owner="owner" :repo="repo" />
  
      <!-- ─────── CONTENT (RIGHT) ─────── -->
      <div class="flex-1 p-6 space-y-8 max-w-7xl mx-auto">
        <!-- ─────── TITLE ROW ─────── -->
        <h2 class="text-2xl font-bold text-gray-800">
          {{ dashboard?.title || 'Saved dashboard' }}
        </h2>
  
        <!-- ─────── TIMEFRAME FILTER CARD ─────── -->
        <div class="bg-white p-4 rounded-2xl shadow">
          <h3 class="text-lg font-semibold text-gray-700 mb-2">
            Select Timeframe
          </h3>
  
          <div class="flex gap-4">
            <button
              v-for="option in ['day', 'week', 'month']"
              :key="option"
              @click="frame = option"
              :class="[
                'px-5 py-2 rounded-full text-sm font-medium transition-colors duration-200',
                frame === option
                  ? 'bg-blue-600 text-white shadow'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              {{ option[0].toUpperCase() + option.slice(1) }}
            </button>
          </div>
        </div>
  
        <!-- ─────── DASHBOARD CONTENT ─────── -->
        <template v-if="dashboard && dashboard.metrics.length">
          <!-- KPI cards -->
          <div v-if="topMetrics.length" class="grid gap-4 md:grid-cols-3">
            <MetricCard
              v-for="item in topMetrics"
              :key="item.id"
              :title="metricMap[item.id]?.label"
              :value="getValue(item)"
            />
          </div>
  
          <!-- Graphs -->
          <div v-if="graphMetrics.length" class="grid gap-4 md:grid-cols-2">
            <component
              v-for="item in graphMetrics"
              :key="item.id"
              :is="widget(metricMap[item.id]?.graph)"
              :title="metricMap[item.id]?.label"
              :series="getValue(item)"
              class="w-full"
            />
          </div>
        </template>
  
        <p v-else class="text-gray-500">
          This dashboard is empty or was not found.
        </p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted, watch, onUnmounted } from 'vue'
  import { useRoute } from 'vue-router'
  import MenuCard     from '@/components/MenuCard.vue'
  import MetricCard   from '@/components/MetricCard.vue'
  import LineAreaCard from '@/components/LineAreaCard.vue'
  import BarAreaCard  from '@/components/BarAreaCard.vue'
  
  /* ───────── route & reactive params ───────── */
  const route = useRoute()
  const owner = route.params.owner
  const repo  = route.params.repo
  
  /* reactive id so the page updates when the URL changes */
  const dashboardId = computed(() => String(route.params.id))
  
  /* ───────── component state ───────── */
  const dashboard  = ref(null)
  const available  = ref([])
  const dataFiles  = reactive({})
  const frame      = ref('month')   // timeframe selector
  
  /* ───────── helpers ───────── */
  function loadDashboard () {
    const all = JSON.parse(localStorage.getItem('savedDashboards') || '[]')
    dashboard.value = all.find(d => String(d.id) === dashboardId.value) || null
  }
  
  /* load again if user saves/updates dashboards while we are on this page */
  function handleUpdateEvent () {
    loadDashboard()
  }
  
  /* ───────── metric helpers ───────── */
  const metricMap = computed(() =>
    Object.fromEntries(available.value.map(m => [m.id, m]))
  )
  
  const topMetrics = computed(() =>
    (dashboard.value?.metrics || []).filter(
      m => metricMap.value[m.id]?.graph === 'metric'
    )
  )
  
  const graphMetrics = computed(() =>
    (dashboard.value?.metrics || []).filter(
      m => metricMap.value[m.id]?.graph !== 'metric'
    )
  )
  
  function widget (type = '') {
    const t = (type || '').toLowerCase()
    if (t === 'metric')          return MetricCard
    if (t === 'line')            return LineAreaCard
    if (t.startsWith('bar'))     return BarAreaCard
    if (t.startsWith('area'))    return LineAreaCard
    return 'div'
  }
  
  /* ───────── value resolver ───────── */
  function scalarFromEntry (entry) {
    if (typeof entry === 'number') return entry
    if (Array.isArray(entry) && entry.length) {
      const last = entry[entry.length - 1]
      if (typeof last === 'number') return last
      if (typeof last === 'object' && 'y' in last) return last.y
    }
    if (entry && typeof entry === 'object') {
      return scalarFromEntry(entry[frame.value])
    }
    return null
  }
  
  function getValue (item) {
    const rawPath = metricMap.value[item.id]?.path
    if (!rawPath) return []
  
    let file, key
    if (rawPath.includes('>')) {
      [file, key] = rawPath.split('>').map(s => s.trim())
    } else {
      [file, key] = rawPath.split('/').map(s => s.trim())
    }
    if (!file || !key) return []
  
    if (!dataFiles[file]) {
      fetch('/' + file)
        .then(r => r.json())
        .then(j => (dataFiles[file] = j))
        .catch(() => (dataFiles[file] = {}))
      return []
    }
  
    const graphType = (metricMap.value[item.id]?.graph || '').toLowerCase()
    const entry     = dataFiles[file]?.[key]
    if (!entry) return []
  
    if (graphType === 'metric') return scalarFromEntry(entry)
    if (entry?.[frame.value])   return entry[frame.value]
    if (typeof entry === 'object' && !Array.isArray(entry))
      return Object.entries(entry).map(([x, y]) => ({ x, y }))
    if (Array.isArray(entry))   return entry
  
    return []
  }
  
  /* ───────── initial + reactive loading ───────── */
  onMounted(async () => {
    const res       = await fetch('/metricsDescription.json')
    available.value = await res.json()
    loadDashboard()
    window.addEventListener('dashboards-updated', handleUpdateEvent)
  })
  
  watch(dashboardId, () => {
    // URL changed (user clicked another saved dashboard)
    loadDashboard()
  })
  
  onUnmounted(() => {
    window.removeEventListener('dashboards-updated', handleUpdateEvent)
  })
  </script>
  
  <style scoped>
  /* Tailwind handles the bulk of styling */
  </style>
  