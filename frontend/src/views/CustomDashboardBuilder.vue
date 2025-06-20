<!-- eslint-disable no-irregular-whitespace -->
<template>
  <div class="flex gap-6">
    <!-- ───────── LEFT MENU ───────── -->
    <MenuCard :owner="owner" :repo="repo" />

    <!-- ───────── RIGHT WORKSPACE ───────── -->
    <div class="flex-1 space-y-4">
      <!-- Tabs header -->
      <div class="flex border-b border-gray-200">
        <button
          v-for="t in tabs"
          :key="t"
          @click="activeTab = t"
          class="px-4 py-2 -mb-px font-medium"
          :class="activeTab === t
            ? 'border-b-2 border-indigo-600 text-indigo-600'
            : 'text-gray-500 hover:text-indigo-600'"
        >
          {{ tabLabels[t] }}
        </button>

        <div class="ml-auto flex items-center gap-2 px-4 py-2">
          <input
            v-model="dashboardTitle"
            placeholder="Dashboard title"
            class="border rounded px-2 py-1 text-sm w-48"
          />
          <button
            @click="saveDashboard"
            class="bg-green-600 text-white text-sm px-3 py-1 rounded hover:bg-green-700"
          >
            💾 Save
          </button>
        </div>
      </div>

      <!-- ① LLM CHAT TAB -->
      <div v-if="activeTab === 'chat'" class="h-[75vh] flex flex-col">
        <div class="flex-1 overflow-y-auto space-y-3 rounded-lg border p-4 bg-white">
          <div
            v-for="m in chatMessages"
            :key="m.id"
            :class="m.role === 'user' ? 'text-right' : 'text-left'"
          >
            <p
              class="inline-block px-3 py-2 rounded-lg max-w-[80%]"
              :class="m.role === 'user'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-800'"
              v-html="renderMarkdown(m.content)"
            />
          </div>
        </div>
        <form @submit.prevent="handleSend" class="mt-3 flex">
          <textarea
            v-model="draft"
            rows="2"
            class="flex-1 border rounded-l-lg p-2 resize-none"
            placeholder="Ask the LLM to design a dashboard…"
          />
          <button class="px-4 bg-indigo-600 text-white rounded-r-lg">Send</button>
        </form>
      </div>

      <!-- ② MANUAL BUILDER TAB -->
      <div v-else-if="activeTab === 'builder'" class="flex gap-6">
        <aside class="w-64 space-y-4">
          <button
            v-for="g in groups"
            :key="g"
            @click="selectedGroup = g"
            class="w-full text-left px-3 py-2 rounded-lg border hover:shadow transition capitalize"
            :class="selectedGroup === g
              ? 'bg-indigo-50 ring-2 ring-indigo-500'
              : 'bg-white'"
          >
            {{ g }}
          </button>
        </aside>

        <section v-if="selectedGroup" class="flex-1">
          <h2 class="text-lg font-semibold mb-4 capitalize">
            {{ selectedGroup }} — choose metrics
          </h2>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <label
              v-for="m in metricsForGroup"
              :key="m.id"
              class="border rounded-lg p-3 cursor-pointer hover:shadow flex flex-col gap-1"
              :class="isSelected(m.id)
                ? 'ring-2 ring-indigo-600 bg-indigo-50'
                : 'bg-white'"
            >
              <input
                type="checkbox"
                class="sr-only"
                :checked="isSelected(m.id)"
                @change="toggleMetric(m)"
              />
              <span class="font-medium">{{ m.label }}</span>
              <span class="text-xs text-gray-500">{{ m.description }}</span>
              <span class="text-xs italic text-gray-400">Style: {{ m.graph }}</span>
            </label>
          </div>
        </section>
      </div>

      <!-- ③ PREVIEW TAB -->
      <div v-else-if="activeTab === 'preview'" class="min-h-[75vh] bg-gray-50 rounded-2xl p-6 space-y-8">
        <h3 class="text-lg font-semibold text-gray-700">
          Dashboard preview
        </h3>

        <template v-if="selectedMetrics.length">
          <!-- KPI cards (metrics) -->
          <div v-if="topMetrics.length" class="grid gap-4 md:grid-cols-3">
            <MetricCard
              v-for="item in topMetrics"
              :key="item.id"
              :title="metricMap[item.id]?.label"
              :value="getValue(item)"
            />
          </div>

          <!-- Graphs two‑per‑row -->
          <div v-if="graphMetrics.length" class="grid gap-4 md:grid-cols-2">
            <component
              v-for="item in graphMetrics"
              :key="item.id"
              :is="widgetComponent(metricMap[item.id]?.graph)"
              :title="metricMap[item.id]?.label"
              :series="getValue(item)"
              class="w-full"
            />
          </div>
        </template>

        <p v-else class="text-gray-500">
          Select metrics in the Manual tab to generate a preview.
        </p>
      </div>

      <!-- ③ PREVIEW TAB -->
<div v-else class="min-h-[75vh] bg-gray-50 rounded-2xl p-6 space-y-8">
  <h3 class="text-lg font-semibold text-gray-700">
    LLM‑generated preview
  </h3>

  <template v-if="selectedMetrics.length">
    <!-- KPI cards (metrics) -->
    <div v-if="topMetrics.length" class="grid gap-4 md:grid-cols-3">
      <MetricCard
        v-for="item in topMetrics"
        :key="item.id"
        :title="metricMap[item.id]?.label"
        :value="getValue(item) ?? '-'"
      />
    </div>

    <!-- Graphs two‑per‑row -->
    <div v-if="graphMetrics.length" class="grid gap-4 md:grid-cols-2">
      <component
        v-for="item in graphMetrics"
        :key="item.id"
        :is="widgetComponent(metricMap[item.id]?.graph)"
        :title="metricMap[item.id]?.label"
        :series="getValue(item)"
        class="w-full"
      />
    </div>
  </template>

  <p v-else class="text-gray-500">
    Select metrics in the Manual tab to generate a preview.
  </p>
</div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import MarkdownIt               from 'markdown-it'
import { useRoute }             from 'vue-router'

import MenuCard     from '@/components/MenuCard.vue'
import MetricCard   from '@/components/MetricCard.vue'
import LineAreaCard from '@/components/LineAreaCard.vue'
import BarAreaCard  from '@/components/BarAreaCard.vue'

/* ───────── route + tabs ───────── */
const { owner, repo } = useRoute().params
const tabs      = ['chat', 'builder', 'preview']
const tabLabels = { chat: 'LLM', builder: 'Manual', preview: 'Preview' }
const activeTab = ref('chat')

/* ───────── chat state ───────── */
let   messageId  = 0
const chatMessages = reactive([])
const draft        = ref('')

/* ───────── catalogue + selections ───────── */
const availableMetrics = ref([])        // raw JSON catalogue
const metricMap = computed(() =>
  Object.fromEntries(availableMetrics.value.map(m => [m.id, m]))
)

/* 🔑 keep selections as objects { id, size } everywhere */
const selectedMetrics = ref([])         // reactive dashboard layout

/* ───────── sidebar grouping ───────── */
const groups        = ref([])
const selectedGroup = ref(null)

const dashboardTitle   = ref('')
const savedDashboards  = ref([])

watch(availableMetrics, list => {
  groups.value = [...new Set(list.map(m => m.group || 'ungrouped'))]
  if (!selectedGroup.value) selectedGroup.value = groups.value[0] || null
})

const metricsForGroup = computed(() =>
  availableMetrics.value.filter(m => (m.group || 'ungrouped') === selectedGroup.value))

/* ───────── selection helpers ───────── */
const isSelected = id => selectedMetrics.value.some(m => m.id === id)

function toggleMetric(metric) {
  if (isSelected(metric.id)) {
    selectedMetrics.value = selectedMetrics.value.filter(m => m.id !== metric.id)
  } else {
    selectedMetrics.value.push({
      id  : metric.id,
      size: metric.graph === 'metric' ? 'small' : 'medium'
    })
  }
}

/* ───────── component resolver ───────── */
function widgetComponent(type = '') {
  const t = type.toLowerCase()
  if (t === 'metric') return MetricCard
  if (t === 'line') return LineAreaCard
  if (t.startsWith('bar')) return BarAreaCard
  if (t.startsWith('area')) return LineAreaCard
  return 'div'
}

/* ───────── LLM helper ───────── */
async function queryOllama(userPrompt) {
  const catalogue = availableMetrics.value.map(m => ({ id: m.id, label: m.label }));
  const alreadySelected = selectedMetrics.value.map(id => ({
    id,
    label: metricMap.value[id]?.label || '(label-missing)',
  }));

  const prompt = `
You are part of an interactive dashboard‑builder. Your ONLY task is to choose which metrics best match the user's request.

INSTRUCTIONS
‣ Pick from the catalogue below.
‣ Output **exactly one** of the two actions between dollar‑signs:
    $APPEND$  – add these metrics to the dashboard
    $REMOVE$  – remove these metrics from the dashboard
‣ Immediately after the action, output a JavaScript array with the metric IDs:
    ["metric_id_A", "metric_id_B"]
‣ Finally, write the chat response you want the user to see, enclosed in < >.

Output order **must** be:
    $ACTION$  ARRAY  USER‑MESSAGE

CATALOGUE
${JSON.stringify(catalogue, null, 2)}

METRICS ALREADY SELECTED
${JSON.stringify(alreadySelected, null, 2)}

USER REQUEST
${userPrompt}
`;
  /* the fetch / streaming logic stays the same … */
  try {
    const res = await fetch('http://localhost:11434/api/generate', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ model: 'llama3.1:8b', prompt }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const reader  = res.body.getReader()
    const decoder = new TextDecoder()
    let assistantFull = ''
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      decoder.decode(value, { stream: true })
            .split('\n')
            .filter(Boolean)
            .forEach(line => {
              try {
                const obj = JSON.parse(line)
                if (obj.response) assistantFull += obj.response
              } catch {
                /* Ignore */
              }
            })
    }
    return assistantFull
  } catch (err) {
    chatMessages.push({
      id: messageId++, role: 'assistant',
      content: `**Virtual Assistant** 🧠\nError: ${err.message}`
    })
  }
}

/* ───────── chat handler ───────── */
async function handleSend() {
  const content = draft.value.trim()
  if (!content) return

  /* 1 ─ push user message */
  chatMessages.push({ id: messageId++, role: 'user', content })
  draft.value = ''

  /* 2 ─ ask Ollama */
  const raw = await queryOllama(content)
  if (!raw) return

  /* 3 ─ parse  $ACTION$ [ids] <message> */
  const act   = raw.match(/\$(APPEND|REMOVE)\$/)?.[1]   // APPEND or REMOVE
  let   ids   = []
  try {
    ids = JSON.parse('[' + (raw.match(/\[([^\]]+)\]/)?.[1] ?? '') + ']')
  } catch {/* malformed array → leave empty */}

  const reply = raw.match(/<([\s\S]+?)>/)?.[1]?.trim()  // friendly text

  /* 4 ─ show the friendly chat response, if any */
  if (reply) {
    chatMessages.push({
      id: messageId++,
      role: 'assistant',
      content: `**Virtual Assistant** 🧠\n${reply}`
    })
  }

  if (!act || !ids.length) return        // nothing to do

  /* pretty names for logs */
  const titles = ids.map(id => metricMap.value[id]?.label || id)

  /* 5 ─ mutate selection + technical feedback */
  if (act === 'REMOVE') {
    selectedMetrics.value = selectedMetrics.value.filter(m => !ids.includes(m.id))

    chatMessages.push({
      id: messageId++,
      role: 'assistant',
      content: `**Virtual Assistant** 🧠\nMetrics removed: ${titles.join(', ')}.`
    })

  } else if (act === 'APPEND') {
    const newbies = ids.filter(id => !selectedMetrics.value.some(m => m.id === id))

    if (newbies.length) {
      selectedMetrics.value.push(
        ...newbies.map(id => ({
          id,
          size: metricMap.value[id]?.graph === 'metric' ? 'small' : 'medium'
        }))
      )

      /* build a quick description block */
      const descLines = newbies.flatMap(id => {
        const m = metricMap.value[id]
        if (!m) return []
        return [`• **${m.label}**`, m.description ? `  ${m.description}` : '', '']
      }).join('\n')

      chatMessages.push({
        id: messageId++,
        role: 'assistant',
        content: `**Virtual Assistant** 🧠\nHere is a brief description:\n${descLines}`
      })

    } else {
      /* user asked for metrics that were already there */
      chatMessages.push({
        id: messageId++,
        role: 'assistant',
        content: `**Virtual Assistant** 🧠\nAll requested metrics were already selected.`
      })
    }
  }
}


/* ───────── preview helpers ───────── */
const topMetrics   = computed(() => selectedMetrics.value
  .filter(m => metricMap.value[m.id]?.graph === 'metric'))
const graphMetrics = computed(() => selectedMetrics.value
  .filter(m => metricMap.value[m.id]?.graph !== 'metric'))

const dataFiles = reactive({})          // { 'engagementAnalysis.json': { … } }

/* ───────── strong-typed getValue ───────── */
function getValue(item) {
  const rawPath = metricMap.value[item.id]?.path;
  if (!rawPath) return [];

  // Split path
  let file, key;
  if (rawPath.includes('>')) {
    [file, key] = rawPath.split('>').map(s => s.trim());
  } else {
    [file, key] = rawPath.split('/').map(s => s.trim());
  }
  if (!file || !key) return [];

  // Lazy-load data
  if (!dataFiles[file]) {
    fetch('/' + file)
      .then(r => r.json())
      .then(json => (dataFiles[file] = json))
      .catch(() => (dataFiles[file] = {}));
    return [];
  }

  const frame = "month"; // "month" | "week" | "day"
  const graphType = metricMap.value[item.id]?.graph?.toLowerCase();
  const entry = dataFiles[file]?.[key];

  // CASE 1 ▸ Not found yet
  if (!entry) return [];

  // CASE 2 ▸ Frame-based: { day: [...], month: [...], week: [...] }
  if (entry?.[frame]) return entry[frame];

  // CASE 3 ▸ Object: { x1: y1, x2: y2 } ➝ [{ x, y }]
  if (typeof entry === 'object' && !Array.isArray(entry)) {
    return Object.entries(entry).map(([x, y]) => ({ x, y }));
  }

  // CASE 4 ▸ Array (already correct shape for charts)
  if (Array.isArray(entry)) return entry;

  // CASE 5 ▸ Scalar metric (for cards)
  if (graphType === 'metric') {
    return typeof entry === 'number' ? entry : null;
  }

  return []; // fallback safe shape
}

/* ───────── watcher for debug ───────── */
watch(selectedMetrics, v =>
  console.log('▶︎ selectedMetrics', JSON.parse(JSON.stringify(v)))
, { deep: true })

/* ───────── initial load ───────── */
onMounted(async () => {
  const res = await fetch('/metricsDescription.json')
  availableMetrics.value = await res.json()
  chatMessages.push({
    id: messageId++, role: 'assistant',
    content:
        `**Virtual Assistant** 🧠\n` +
        `Welcome! Tell me what insights you need and I’ll add the best metrics. \n` +
        `If you ever wonder how a metric is calculated, feel free to ask me! `
    })
})

/* ───────── markdown helper ───────── */
const md = new MarkdownIt({ breaks: true, linkify: true, html: false })
const renderMarkdown = txt => md.render(txt || '')

function saveDashboard() {
  const name = dashboardTitle.value.trim()
  if (!name) {
    alert('Please enter a dashboard title.')
    return
  }

  const payload = {
    id      : Date.now().toString(),      // unique ID ⇢ string safer for routing
    title   : name,
    metrics : JSON.parse(JSON.stringify(selectedMetrics.value)),
    tsSaved : Date.now()
  }

  const all = JSON.parse(localStorage.getItem('savedDashboards') || '[]')
  all.push(payload)
  localStorage.setItem('savedDashboards', JSON.stringify(all))

  savedDashboards.value = all
  dashboardTitle.value  = ''
  window.dispatchEvent(new Event('dashboards-updated'))
  alert(`Dashboard "${name}" saved.`)
}

</script>