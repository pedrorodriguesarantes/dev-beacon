<template>
  <div class="flex gap-6">
    <!-- ─────────── PERSISTENT LEFT MENU ─────────── -->
    <MenuCard :owner="owner" :repo="repo" />

    <!-- ─────────── RIGHT WORKSPACE ─────────── -->
    <div class="flex-1 space-y-4">
      <!-- Tabs -->
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
            >
              {{ m.content }}
            </p>
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

      <!-- ② MANUAL PICKER TAB -->
      <div v-else-if="activeTab === 'builder'" class="flex gap-6">
        <!-- Group rail -->
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

        <!-- Metric chooser -->
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
                @change="toggleMetric(m.id)"
              />
              <span class="font-medium">{{ m.label }}</span>
              <span class="text-xs text-gray-500">{{ m.description }}</span>
              <span class="text-xs italic text-gray-400">Style: {{ m.graph }}</span>
            </label>
          </div>
        </section>
      </div>

      <!-- ③ PREVIEW TAB -->
      <div v-else class="min-h-[75vh] bg-gray-50 rounded-2xl p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-700">
          LLM‑generated preview
        </h3>
        <div
          v-if="selectedMetrics.length"
          class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
        >
          <component
            v-for="id in selectedMetrics"
            :key="id"
            :is="widgetComponent(metricMap[id]?.type || 'div')"
            v-bind="metricMap[id]?.props"
          />
        </div>
        <p v-else class="text-gray-500">
          Ask something in the LLM tab to generate a preview.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-unused-vars */
import { ref, reactive, computed, onMounted, watch } from 'vue';
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

/* ── metrics catalogue ────────────────────────────────────────── */
const availableMetrics = ref([]);
const metricMap = computed(() =>
  Object.fromEntries(availableMetrics.value.map(m => [m.id, m]))
);
const selectedMetrics = ref([]);  // IDs ticked by user or suggested by LLM

/* ── grouping helpers ─────────────────────────────────────────── */
const groups        = ref([]);    // e.g. ['issues', 'pull_request']
const selectedGroup = ref(null);

watch(availableMetrics, list => {
  groups.value = [...new Set(list.map(m => m.group || 'ungrouped'))];
  if (!selectedGroup.value) selectedGroup.value = groups.value[0] || null;
});

/* metrics in the active group */
const metricsForGroup = computed(() =>
  availableMetrics.value.filter(
    m => (m.group || 'ungrouped') === selectedGroup.value
  )
);

/* picker helpers */
const isSelected = id => selectedMetrics.value.includes(id);
function toggleMetric(id) {
  if (isSelected(id)) {
    selectedMetrics.value = selectedMetrics.value.filter(x => x !== id);
  } else {
    selectedMetrics.value.push(id);
  }
}

/* component mapping for Preview tab (adjust if needed) */
function widgetComponent(t) {
  if (t === 'metric') return MetricCard;
  if (t === 'line')   return LineChart;
  if (t === 'bar')    return BarAreaCard;
  return 'div';
}

/* ── Ollama interaction (unchanged) ──────────────────────────── */
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

  try {
    const res = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'llama3.1:8b', prompt }),
    });

    if (!res.ok) {
      chatMessages.push({ id: messageId++, role: 'assistant', content: `Error: HTTP ${res.status}` });
      return;
    }

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let assistantFull = '';

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
    return [{ id: messageId++, role: 'assistant', content: assistantFull }];
  } catch (err) {
    chatMessages.push({ id: messageId++, role: 'assistant', content: `Error: ${err.message}` });
  }
}

async function handleSend() {
  const content = draft.value.trim();
  if (!content) return;

  chatMessages.push({ id: messageId++, role: 'user', content });
  draft.value = '';

  const message = await queryOllama(content);
  const last = message?.at(-1);
  if (!last || last.role !== 'assistant') return;

  const txt      = last.content;
  const actMatch = txt.match(/\$(APPEND|REMOVE)\$/);
  const arrMatch = txt.match(/\[([^\]]+)\]/);
  if (!actMatch || !arrMatch) return;

  let ids = [];
  try { ids = JSON.parse('[' + arrMatch[1] + ']'); } catch (e) { /* ignore */ }
  const action = actMatch[1];
  const titles = ids.map(id => metricMap.value[id]?.label || id);

  if (action === 'REMOVE') {
    selectedMetrics.value = selectedMetrics.value.filter(id => !ids.includes(id));
    chatMessages.push({ id: messageId++, role: 'assistant', content: `Metrics Removed: ${titles.join(', ')}.` });
  } else {
    const newIds = ids.filter(id => !selectedMetrics.value.includes(id));
    selectedMetrics.value.push(...newIds);
    chatMessages.push({ id: messageId++, role: 'assistant', content: `Metrics Added: ${titles.join(', ')}.` });

    chatMessages.push({ id: messageId++, role: 'assistant', content: 'Here is a brief description:' });
    const descLines = newIds.flatMap(id => {
      const m = metricMap.value[id];
      if (!m) return [];
      return [`• ${m.label}`, `  ${m.description || 'No description.'}`, ''];
    }).join('\n');
    chatMessages.push({ id: messageId++, role: 'assistant', content: descLines });
    chatMessages.push({ id: messageId++, role: 'assistant', content: 'If you have questions about how each metric is calculated, you can check the information section located upper right on each graph.' });
  }

  chatMessages.push(...message);
}

/* ── initial load ─────────────────────────────────────────────── */
onMounted(async () => {
  try {
    const res = await fetch('/metricsDescription.json');
    availableMetrics.value = await res.json();
  } catch (err) {
    console.error('Failed to load metricsDescription.json:', err);
  }
});
</script>
