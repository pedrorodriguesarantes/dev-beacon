<template>
  <div class="flex gap-6">
    <!-- ─────────────── LEFT : SIDE MENU ─────────────── -->
    <MenuCard :owner="owner" :repo="repo" />

    <!-- ─────────────── RIGHT : MAIN CONTENT ─────────────── -->
    <div class="flex-1 space-y-6">
      <!-- ────────── REPOSITORY HEADER ────────── -->
      <div v-if="projectInfo" class="flex items-center gap-4 bg-white p-4 rounded-2xl shadow">
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
          <h1 class="text-xl font-bold text-gray-700">{{ projectInfo.name }}</h1>
        </a>
      </div>
      <div v-else class="text-red-500 p-4">Repository not found.</div>

      <!-- ────────── Filter Title + Buttons, Centered & Stacked ────────── -->
      <div class="flex flex-col bg-white p-4 rounded-2xl shadow">
        <h3 class="text-lg font-semibold text-gray-700"> Select Timeframe</h3>
        
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
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            title="Total Opened Issues"
            :value="issuesData[`${frameLocal}_opened_last`] ?? 0"
            :trend="issuesData[`trend_opened_${frameLocal}`] ?? 0"
          />

          <MetricCard
            title="Total Closed Issues"
            :value="issuesData[`${frameLocal}_closed_last`] ?? 0"
            :trend="issuesData[`trend_closed_${frameLocal}`] ?? 0"
          />
        </div>

        <!-- ─────── BACKLOG LINE CHART ─────── -->
        <div class="bg-white rounded-2xl p-4 shadow">
          <h3 class="font-semibold text-gray-700">Issues Backlog Size</h3>
          <TimeframeToggle v-model="frameLocal" />
          <LineChart :series="issuesData[`backlog_${frameLocal}s`]" />
        </div>

        <!-- ───────  FOUR AREA CHARTS ─────── -->
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-2">
          <LineAreaCard
            :title="`Opening Issues Rate (${frameLocal})`"
            :series="issuesData[`open_by_${frameLocal}`]"
          />

          <LineAreaCard
            :title="`Closing Issues Rate (${frameLocal})`"
            :series="issuesData[`close_by_${frameLocal}`]"
          />

          <LineAreaCard
            :title="`Time for First Answer (${frameLocal}${frameLocal === 'day' ? ') (Δ hours)' : ') (Δ days)'}`"
            :series="issuesData[`close_by_${frameLocal}`]"
          />

          <LineAreaCard
            :title="`Time for Closing (${frameLocal}${frameLocal === 'day' ? ') (Δ hours)' : ') (Δ days)'}`"
            :series="issuesData[`time_to_close_${frameLocal}`]"
          />
        </div>
      </section>

      <section v-else class="text-gray-400 p-8">
        Loading Issue data for <strong>{{ owner }}/{{ repo }}</strong>...
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
// import TimeframeToggle from '@/components/TimeframeToggle.vue';
// import LabelBarCard from '@/components/LabelBarCard.vue';
import LineChart from '@/components/LineChart.vue';
import LineAreaCard from '@/components/LineAreaCard.vue';

const route = useRoute();
const owner = route.params.owner;
const repo  = route.params.repo;

const repositories = ref([]);
const projectInfo = computed(() => {
  if (!owner || !repo) return null;
  return repositories.value.find(p => {
    return (
      (p.github && p.github.includes(`${owner}/${repo}`)) ||
      (p.owner === owner && p.repo === repo)
    );
  });
});

const frameLocal = ref('month');

// ────────── Initialize issuesData with an empty object
const issuesData = ref({});
const initialized = ref(false);

onMounted(async () => {
  try {
    const response = await axios.get(`/metrics/${owner.toLowerCase()}/${repo.toLowerCase()}/issuesAnalysis.json`);
    issuesData.value = response.data;

    const res = await fetch('/repositories.json');
    repositories.value = await res.json();
  } catch (e) {
    console.error('Failed to load pull-request data:', e);
  } finally {
    initialized.value = true;
  }
});

</script>

<style scoped>
/* Tailwind handles all visuals */
</style>