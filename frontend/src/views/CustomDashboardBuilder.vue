<template>
  <div class="flex gap-6">
    <!-- ─────────── PERSISTENT LEFT MENU (Repo / nav) ─────────── -->
    <MenuCard :owner="owner" :repo="repo" />

    <!-- ─────────── RIGHT WORKSPACE ─────────── -->
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
      </div>

      <!-- ① LLM CHAT TAB -->
      <div v-if="activeTab === 'chat'" class="h-[75vh] flex flex-col">
        <div class="flex-1 overflow-y-auto space-y-3 rounded-lg border p-4 bg-white">
          <div v-for="m in chatMessages" :key="m.id" :class="m.role === 'user' ? 'text-right' : 'text-left'">
            <p
              class="inline-block px-3 py-2 rounded-lg max-w-[80%]"
              :class="m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-800'"
            >
              {{ m.content }}
            </p>
          </div>
        </div>
        <form @submit.prevent="handleSend" class="mt-3 flex">
          <textarea v-model="draft" rows="2" class="flex-1 border rounded-l-lg p-2 resize-none" placeholder="Ask the LLM to design a dashboard…"></textarea>
          <button class="px-4 bg-indigo-600 text-white rounded-r-lg">Send</button>
        </form>
      </div>

      <!-- ② MANUAL BUILDER TAB -->
      <div v-else-if="activeTab === 'builder'" class="flex gap-6">
        <!-- Builder sidebar (widgets + saved) -->
        <aside class="bg-white rounded-2xl p-4 shadow flex flex-col w-56">
          <!-- Widgets palette -->
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Widgets</h3>
          <ul class="space-y-2">
            <li v-for="w in widgets" :key="w.type">
              <button @click="addWidget(w.type)" class="w-full text-left px-2 py-1 rounded-lg bg-gray-100 hover:bg-gray-200">
                {{ w.label }}
              </button>
            </li>
          </ul>
          <hr class="my-4" />
          <!-- Saved dashboards -->
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Saved Dashboards</h3>
          <ul class="flex-1 overflow-y-auto pr-1 space-y-2">
            <li v-for="d in saved" :key="d.name">
              <button @click="loadDashboard(d)" class="w-full text-left px-2 py-1 rounded-lg hover:underline">
                {{ d.name }}
              </button>
            </li>
          </ul>
          <button @click="saveDashboard" class="mt-4 w-full py-2 rounded-lg bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition">
            Save Current
          </button>
        </aside>

        <!-- Drag & drop canvas -->
        <div class="flex-1">
          <grid-layout
            :layout="layout"
            :col-num="12"
            :row-height="30"
            :is-draggable="true"
            :is-resizable="true"
            :vertical-compact="false"
            class="bg-gray-50 rounded-2xl p-4 min-h-[70vh]"
            @layout-updated="onLayoutChange"
          >
            <grid-item
              v-for="item in layout"
              :key="item.i"
              v-bind="item"
              class="bg-white shadow rounded-lg overflow-hidden relative"
            >
              <component :is="widgetComponent(item.type)" v-bind="item.props" />
              <button
                class="absolute top-1 right-1 text-xs bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                @click.stop="removeWidget(item.i)"
              >×</button>
            </grid-item>
          </grid-layout>
        </div>
      </div>

      <!-- ③ PREVIEW TAB -->
      <div v-else class="min-h-[75vh] bg-gray-50 rounded-2xl p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-700">LLM‑generated preview</h3>
        <div v-if="selectedMetrics.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <component
            v-for="id in selectedMetrics"
            :key="id"
            :is="widgetComponent(metricMap[id]?.type || 'div')"
            v-bind="metricMap[id]?.props"
          />
        </div>
        <p v-else class="text-gray-500">Ask something in the LLM tab to generate a preview.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import MenuCard      from '@/components/MenuCard.vue';
import MetricCard    from '@/components/MetricCard.vue';
import LineChart     from '@/components/LineChart.vue';
import BarAreaCard   from '@/components/BarAreaCard.vue';

/* ── route params ─────────────────────────────────────────────── */
const route = useRoute();
const owner = route.params.owner;
const repo  = route.params.repo;

/* ── tabs ─────────────────────────────────────────────────────── */
const tabs      = ['chat', 'builder', 'preview'];
const tabLabels = { chat: 'LLM', builder: 'Manual', preview: 'Preview' };
const activeTab = ref('chat');

/* ── chat state ───────────────────────────────────────────────── */
let messageId = 0;
const chatMessages = reactive([]);
const draft = ref('');

/* ── metrics catalogue (loaded at runtime) ────────────────────── */
const availableMetrics = ref([]);
const metricMap = computed(() =>
  Object.fromEntries(availableMetrics.value.map(m => [m.id, m]))
);
const selectedMetrics = ref([]);   // IDs chosen by the LLM

async function queryOllama(userPrompt) {
  /* ---------- build helper JSON objects ---------- */
  const catalogue = availableMetrics.value.map(m => ({ id: m.id, label: m.label }));

  // <‑‑ NEW: everything the user is already seeing on the dashboard
  const alreadySelected = selectedMetrics.value.map(id => ({
    id,
    label: metricMap.value[id]?.label || '(label‑missing)'
  }));

  /* ---------- build the big prompt ---------- */
  const prompt = `
    You are part of an interactive dashboard‑builder. Your ONLY task is to
    choose which metrics best match the user's request.

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

  try {
    const res = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'llama3.1:8b', prompt }),
    });

    if (!res.ok) {
      chatMessages.push({
        id: messageId++,
        role: 'assistant',
        content: `Error: HTTP ${res.status}`,
      });
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let assistantFull = '';

    // read ND‑JSON stream
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      chunk.split('\n').forEach(line => {
        if (!line.trim()) return;
        try {
          const obj = JSON.parse(line);
          if (obj.response) assistantFull += obj.response;
        } catch {/* ignore malformed lines */}
      });
    }

    // chatMessages.push({ id: messageId++, role: 'assistant', content: assistantFull })
    return [{ id: messageId++, role: 'assistant', content: assistantFull }];
  } catch (err) {
    chatMessages.push({ id: messageId++, role: 'assistant', content: `Error: ${err.message}` });
  }
}

async function handleSend() {
  const content = draft.value.trim();
  if (!content) return;

  // user bubble
  chatMessages.push({ id: messageId++, role: 'user', content });
  draft.value = '';

  // ask the LLM
  let message = await queryOllama(content);

  /* ── post‑process assistant reply ───────────────────────── */
  const last = message.at(-1);
  if (!last || last.role !== 'assistant') return;

  const txt       = last.content;
  const actMatch  = txt.match(/\$(APPEND|REMOVE)\$/);
  const arrMatch  = txt.match(/\[([^\]]+)\]/);
  if (!actMatch || !arrMatch) return;

  let ids = [];
  try { ids = JSON.parse('[' + arrMatch[1] + ']'); } catch { /* malformed */ }

  const action = actMatch[1];             // APPEND  |  REMOVE
  const titles = ids.map(id => metricMap.value[id]?.label || id);

  if (action === 'REMOVE') {
    /* remove from dashboard + summary line */
    selectedMetrics.value = selectedMetrics.value.filter(id => !ids.includes(id));
    chatMessages.push({
      id: messageId++,
      role: 'assistant',
      content: `Metrics Removed: ${titles.join(', ')}.`
    });
  } else /* APPEND */ {
    /* add new metrics */
    const newIds = ids.filter(id => !selectedMetrics.value.includes(id));
    selectedMetrics.value.push(...newIds);

    /* summary line */
    chatMessages.push({
      id: messageId++,
      role: 'assistant',
      content: `Metrics Added: ${titles.join(', ')}.`
    });

    chatMessages.push({ 
      id: messageId++, 
      role: 'assistant', 
      content: 'Here is a brief description:'
    });

    const descLines = [
      ...newIds.flatMap(id => {
        const m = metricMap.value[id];
        if (!m) return [];
        return [
          `• ${m.label}`,
          `  ${m.description || 'No description.'}`,
          ''
        ];
      })
    ].join('\n');

    chatMessages.push({ 
      id: messageId++, 
      role: 'assistant', 
      content: descLines
    });

    chatMessages.push({ 
      id: messageId++, 
      role: 'assistant', 
      content: 'If you have questions about how each metric is calculated, you can check the information section located upper right on each graph.'
    });
  }
}


/* ── manual builder (unchanged) ──────────────────────────────── */
const widgets = [
  { type: 'metric', label: 'Metric Card' },
  { type: 'line',   label: 'Line Chart' },
  { type: 'bar',    label: 'Bar / Area Chart' },
];

const layout = ref([]);
const seq    = ref(0);
const saved  = ref([]);

function widgetComponent(type) {
  if (type === 'metric') return MetricCard;
  if (type === 'line')   return LineChart;
  if (type === 'bar')    return BarAreaCard;
  return 'div';
}
function addWidget(type) {
  layout.value.push({ i: `${seq.value++}`, x: 0, y: 0, w: 4, h: 4, type, props: {} });
}
function removeWidget(id) {
  layout.value = layout.value.filter(it => it.i !== id);
}
function onLayoutChange(newLayout) {
  layout.value = newLayout.map(item => ({ ...layout.value.find(l => l.i === item.i), ...item }));
}
function saveDashboard() {
  const name = prompt('Name your dashboard version:');
  if (!name) return;
  const lib = JSON.parse(localStorage.getItem('dashboards') || '[]');
  lib.push({ name, layout: layout.value });
  localStorage.setItem('dashboards', JSON.stringify(lib));
  saved.value = lib;
}
function loadDashboard(d) {
  layout.value = JSON.parse(JSON.stringify(d.layout));
}

/* ── initial load ─────────────────────────────────────────────── */
onMounted(async () => {
  try {
    const res = await fetch('/metricsDescription.json');
    availableMetrics.value = await res.json();
  } catch (err) {
    console.error('Failed to load metricsDescription.json:', err);
  }
  saved.value = JSON.parse(localStorage.getItem('dashboards') || '[]');
});
</script>
