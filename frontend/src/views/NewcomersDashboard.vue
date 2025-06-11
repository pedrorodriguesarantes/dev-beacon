<template>
    <div class="flex gap-6">
      <!-- ─────────────── LEFT : SIDE MENU ─────────────── -->
      <MenuCard :owner="owner" :repo="repo" />
  
      <!-- ─────────────── RIGHT : MAIN CONTENT ─────────────── -->
      <div class="flex-1 space-y-6">
        <!-- ────────── REPOSITORY HEADER ────────── -->
        <div v-if="projectInfo" class="flex items-center gap-4 bg-white p-4 rounded-2xl shadow">
          <a :href="projectInfo.github" target="_blank" class="flex items-center gap-4 hover:opacity-80">
            <img :src="projectInfo.image" :alt="`${projectInfo.name} logo`" class="w-14 h-14 rounded-lg object-contain" />
            <h1 class="text-xl font-bold text-gray-700">{{ projectInfo.name }}</h1>
          </a>
        </div>
        <div v-else class="text-red-500 p-4">Repository not found.</div>
  
        <!-- ────────── TIMEFRAME TOGGLE ────────── -->
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
  
        <!-- ────────── DASHBOARD ────────── -->
        <section v-if="initialized" class="space-y-4">
          <!-- ─────── KPI CARDS ─────── -->
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              title="Newcomers (latest)"
              :value="kpis.totalNewcomers"
              :trend="kpis.trendNewcomers"
              :valueBefore="kpis.prevNewcomers"
            />
            <MetricCard
              title="90‑day Retention (%)"
              :value="kpis.lastRetention"
              :trend="kpis.trendRetention"
              :valueBefore="kpis.prevRetention"
            />
            <MetricCard
              title="Onboarding Success (%)"
              :value="kpis.lastSuccess"
              :trend="kpis.trendSuccess"
              :valueBefore="kpis.prevSuccess"
            />
            <MetricCard
              title="Median Time to 2nd Contrib. (days)"
              :value="kpis.lastTimeToSecond"
              :trend="kpis.trendTimeToSecond"
              :valueBefore="kpis.prevTimeToSecond"
            />
          </div>
  
          <!-- ─────── LINE CHARTS ─────── -->
          <div class="bg-white rounded-2xl p-4 shadow">
            <h3 class="font-semibold text-gray-700">Newcomer Count</h3>
            <LineChart :series="series.newcomers" />
          </div>
  
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-2">
            <BarAreaCard :title="`90‑day Retention (${frameLocal})`" :series="series.retention" />
            <BarAreaCard :title="`Onboarding Success (${frameLocal})`" :series="series.success" />
            <BarAreaCard :title="`Median Time to 2nd Contribution (${frameLocal})`" :series="series.timeToSecond" />
          </div>
        </section>
  
        <section v-else class="text-gray-400 p-8">
          Loading newcomer data for <strong>{{ owner }}/{{ repo }}</strong>...
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
  //import LineAreaCard from '@/components/LineAreaCard.vue';
  
  /* ───────── ROUTE + PROJECT INFO ───────── */
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
  
  /* ───────── STATE ───────── */
  const frameLocal = ref('month');
  const newcomerData = ref({});
  const initialized = ref(false);
  
  /* ───────── HELPERS ───────── */
  const safe = v => (v === null || v === undefined ? 0 : Number(v));
  
  function flattenDay(arr) {
    return Array.isArray(arr) && Array.isArray(arr[0]) ? arr[0] : arr;
  }
  
  function lastNonNull(series) {
    for (let i = series.length - 1; i >= 0; i--) {
      const v = series[i].y;
      if (v !== null && v !== undefined) return Number(v);
    }
    return null;
  }
  
  function secondLastNonNull(series) {
    let found = 0;
    for (let i = series.length - 1; i >= 0; i--) {
      const v = series[i].y;
      if (v !== null && v !== undefined) {
        found++;
        if (found === 2) return Number(v);
      }
    }
    return null;
  }
  
  /* ───────── KPI COMPUTATION ───────── */
  const kpis = computed(() => {
    if (!newcomerData.value.newcomers_count) return {};
  
    const ncSeries = frameLocal.value === 'day'
      ? flattenDay(newcomerData.value.newcomers_count[frameLocal.value])
      : newcomerData.value.newcomers_count[frameLocal.value];
    const retSeries = newcomerData.value.retention_90d[frameLocal.value] || [];
    const sucSeries = newcomerData.value.onboarding_success[frameLocal.value] || [];
    const t2Series  = newcomerData.value.median_time_to_second_contribution[frameLocal.value] || [];
  
    const currNc  = safe(lastNonNull(ncSeries));
    const prevNc  = safe(secondLastNonNull(ncSeries));
    const currRet = safe(lastNonNull(retSeries));
    const prevRet = safe(secondLastNonNull(retSeries));
    const currSuc = safe(lastNonNull(sucSeries));
    const prevSuc = safe(secondLastNonNull(sucSeries));
    const currT2  = safe(lastNonNull(t2Series));
    const prevT2  = safe(secondLastNonNull(t2Series));
  
    const ratio = (curr, prev) => {
      if (prev === 0) return 0;
      return (curr - prev) / Math.abs(prev);
    };
  
    return {
      totalNewcomers: currNc,
      prevNewcomers: prevNc,
      trendNewcomers: ratio(currNc, prevNc),
      lastRetention: currRet,
      prevRetention: prevRet,
      trendRetention: ratio(currRet, prevRet),
      lastSuccess: currSuc,
      prevSuccess: prevSuc,
      trendSuccess: ratio(currSuc, prevSuc),
      lastTimeToSecond: currT2,
      prevTimeToSecond: prevT2,
      trendTimeToSecond: ratio(currT2, prevT2)
    };
  });
  
  /* ───────── SERIES FOR CHARTS ───────── */
  const series = computed(() => {
    if (!newcomerData.value.newcomers_count) return {};
    return {
      newcomers: frameLocal.value === 'day'
        ? flattenDay(newcomerData.value.newcomers_count[frameLocal.value])
        : newcomerData.value.newcomers_count[frameLocal.value],
      retention: newcomerData.value.retention_90d[frameLocal.value] || [],
      success: newcomerData.value.onboarding_success[frameLocal.value] || [],
      timeToSecond: newcomerData.value.median_time_to_second_contribution[frameLocal.value] || []
    };
  });
  
  /* ───────── DATA FETCH ───────── */
  onMounted(async () => {
    try {
      const resData = await axios.get('/newcomerAnalysis.json');
      newcomerData.value = resData.data;
  
      const projRes = await fetch('/repositories.json');
      repositories.value = await projRes.json();
    } catch (err) {
      console.error('Failed to load newcomer data:', err);
    } finally {
      initialized.value = true;
    }
  });
  </script>
  
  <style scoped>
  /* Tailwind handles visuals */
  </style>
  