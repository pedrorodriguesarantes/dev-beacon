<template>
    <div class="flex gap-6">
      <!-- LEFT : SIDE MENU -->
      <MenuCard :owner="owner" :repo="repo" />
  
      <!-- RIGHT : MAIN CONTENT -->
      <div class="flex-1 space-y-6">
        <!-- REPOSITORY HEADER -->
        <div v-if="projectInfo" class="flex items-center gap-4 bg-white p-4 rounded-2xl shadow">
          <a :href="projectInfo.github" target="_blank" class="flex items-center gap-4 hover:opacity-80">
            <img :src="projectInfo.image" :alt="`${projectInfo.name} logo`" class="w-14 h-14 rounded-lg object-contain" />
            <h1 class="text-xl font-bold text-gray-700">{{ projectInfo.name }}</h1>
          </a>
        </div>
        <div v-else class="text-red-500 p-4">Repository not found.</div>
  
        <!-- TIMEFRAME TOGGLE -->
        <div class="flex flex-col bg-white p-4 rounded-2xl shadow">
          <h3 class="text-lg font-semibold text-gray-700">Select Timeframe</h3>
          <div class="inline-flex gap-4">
            <button
              v-for="option in ['day', 'week', 'month']"
              :key="option"
              @click="frameLocal = option"
              :class="[
                'px-4 py-2 rounded-full transition-colors duration-300',
                frameLocal === option
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              {{ option.charAt(0).toUpperCase() + option.slice(1) }}
            </button>
          </div>
        </div>
  
        <!-- DASHBOARD -->
        <section v-if="initialized" class="space-y-4">
          <!-- KPI CARDS -->
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              title="Chat Participation (%)"
              :value="kpis.chatRate"
              :trend="kpis.trendChatRate"
              :valueBefore="kpis.prevChatRate"
            />
            <MetricCard
              title="Committer Churn (%)"
              :value="kpis.committerChurn"
            />
            <MetricCard
              title="Committer Gini"
              :value="kpis.giniLatest"
              :trend="kpis.trendGini"
              :valueBefore="kpis.prevGini"
            />
          </div>
  
          <!-- LINE / BAR CHARTS -->
          <div class="bg-white rounded-2xl p-4 shadow">
            <h3 class="font-semibold text-gray-700">Chat Participation</h3>
            <LineChart :series="series.chat" />
          </div>
  
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-2">
            <BarAreaCard :title="`Committer Concentration Gini (${frameLocal})`" :series="series.gini" />
            <BarAreaCard title="Contributor Count (Yearly)" :series="series.contributors" />
            <BarAreaCard title="Occasional Contributor Count" :series="series.occasional" />
          </div>
        </section>
  
        <section v-else class="text-gray-400 p-8">
          Loading engagement data for <strong>{{ owner }}/{{ repo }}</strong>...
        </section>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import axios from 'axios';
  
  import MenuCard from '@/components/MenuCard.vue';
  import MetricCard from '@/components/MetricCard.vue';
  import LineChart from '@/components/LineChart.vue';
  import BarAreaCard from '@/components/BarAreaCard.vue';
  
  /* ROUTE + PROJECT INFO */
  const route = useRoute();
  const owner = route.params.owner;
  const repo  = route.params.repo;
  
  const repositories = ref([]);
  const projectInfo = computed(() => {
    if (!owner || !repo) return null;
    return repositories.value.find(p =>
      (p.github && p.github.includes(`${owner}/${repo}`)) ||
      (p.owner === owner && p.repo === repo)
    );
  });
  
  /* STATE */
  const frameLocal = ref('month');
  const engagementData = ref({});
  const initialized = ref(false);
  
  /* HELPERS */
  const safe = v => (v === null || v === undefined ? 0 : Number(v));
  function lastNonNull(series) {
    for (let i = series.length - 1; i >= 0; i--) {
      const v = series[i]?.y;
      if (v !== null && v !== undefined) return Number(v);
    }
    return null;
  }
  function secondLastNonNull(series) {
    let found = 0;
    for (let i = series.length - 1; i >= 0; i--) {
      const v = series[i]?.y;
      if (v !== null && v !== undefined) {
        found++;
        if (found === 2) return Number(v);
      }
    }
    return null;
  }
  
  /* KPI COMPUTATION */
  const kpis = computed(() => {
    if (!engagementData.value.active_chat_participation_rate) return {};
  
    const chatSeries = engagementData.value.active_chat_participation_rate[frameLocal.value] || [];
    const labelSeries = engagementData.value.avg_labels_per_open_issue?.[frameLocal.value] || [];
    const giniSeries = engagementData.value.committer_concentration_gini?.[frameLocal.value] || [];
  
    const currChat = safe(lastNonNull(chatSeries));
    const prevChat = safe(secondLastNonNull(chatSeries));
    const currLbl = safe(lastNonNull(labelSeries));
    const prevLbl = safe(secondLastNonNull(labelSeries));
    const currGini = safe(lastNonNull(giniSeries));
    const prevGini = safe(secondLastNonNull(giniSeries));
  
    const ratio = (curr, prev) => (prev === 0 ? 0 : (curr - prev) / Math.abs(prev));
  
    return {
      chatRate: currChat,
      prevChatRate: prevChat,
      trendChatRate: ratio(currChat, prevChat),
  
      avgLabels: currLbl,
      prevLabels: prevLbl,
      trendLabels: ratio(currLbl, prevLbl),
  
      committerChurn: engagementData.value.committer_churn_rate ?? null,
  
      giniLatest: currGini,
      prevGini: prevGini,
      trendGini: ratio(currGini, prevGini),
    };
  });
  
  /* SERIES FOR CHARTS */
  const series = computed(() => {
    if (!engagementData.value.active_chat_participation_rate) return {};
    return {
      chat: engagementData.value.active_chat_participation_rate[frameLocal.value] || [],
      labels: engagementData.value.avg_labels_per_open_issue?.[frameLocal.value] || [],
      gini: engagementData.value.committer_concentration_gini?.[frameLocal.value] || [],
      occasional: engagementData.value.occasional_contributors?.[frameLocal.value] || [],
      contributors: engagementData.value.contributor_counts_yoy || [],
    };
  });
  
  /* DATA FETCH */
  onMounted(async () => {
    try {
      const res = await axios.get('/engagementAnalysis.json');
      engagementData.value = res.data;
  
      const projRes = await fetch('/repositories.json');
      repositories.value = await projRes.json();
    } catch (err) {
      console.error('Failed to load engagement data:', err);
    } finally {
      initialized.value = true;
    }
  });
  </script>
  
  <style scoped>
  /* Tailwind handles visuals */
  </style>
  