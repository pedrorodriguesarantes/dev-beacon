<!-- src/views/Contribute.vue -->
<template>
    <div class="min-h-screen bg-gray-50 py-12 px-6">
      <!-- ─────────────── HERO / INTRO ─────────────── -->
      <section class="max-w-4xl mx-auto text-center space-y-4">
        <h1 class="text-3xl font-extrabold tracking-tight">
          Contribute &nbsp;🤝
        </h1>
        <p class="text-gray-600 leading-relaxed">
          This project aims to help maintainers and contributors understand
          community behavior, developer retention, and overall project health
          through open‑source analytics dashboards.
          <br />
          We believe that <strong>transparent data</strong> and
          <strong>collaborative science</strong> power healthier software
          ecosystems.
        </p>
  
        <!-- CTA button that jumps to the GitHub repository -->
        <a
          href="https://github.com/your‑org/your‑repo"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-indigo-600 text-white font-semibold shadow hover:bg-indigo-700 transition"
        >
          <span>View the Code on GitHub</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 7h6m0 0v6m0-6l-8 8"
            />
          </svg>
        </a>
      </section>
  
      <!-- ─────────────── 3‑COLUMN INFO CARDS ─────────────── -->
      <section
        class="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto"
      >
        <!-- Goals card -->
        <article
          class="bg-white rounded-2xl shadow p-6 flex flex-col gap-2 hover:shadow-lg transition"
        >
          <h2 class="text-lg font-semibold">Project Goals</h2>
          <p class="text-gray-500 text-sm leading-relaxed">
            • Provide actionable metrics for maintainers.<br />
            • Detect developer turnover early.<br />
            • Promote sustainable OSS governance.
          </p>
        </article>
  
        <!-- Open‑Source card -->
        <article
          class="bg-white rounded-2xl shadow p-6 flex flex-col gap-2 hover:shadow-lg transition"
        >
          <h2 class="text-lg font-semibold">Open‑Source&nbsp;First</h2>
          <p class="text-gray-500 text-sm leading-relaxed">
            All dashboards, extractors, and analysis notebooks are licensed under
            <code class="bg-gray-100 px-1 py-0.5 rounded">MIT</code>. Fork, file
            issues, or open PRs—your ideas shape the roadmap!
          </p>
        </article>
  
        <!-- Lab work card -->
        <article
          class="bg-white rounded-2xl shadow p-6 flex flex-col gap-2 hover:shadow-lg transition"
        >
          <h2 class="text-lg font-semibold">Our Research Lab</h2>
          <p class="text-gray-500 text-sm leading-relaxed">
            The <strong>Open‐Source Health Lab</strong> (Northern Arizona
            University) investigates community dynamics and software ecosystem
            sustainability.
          </p>
          <a
            href="https://oss‑health‑lab.example.edu"
            target="_blank"
            rel="noopener"
            class="mt-auto text-indigo-600 hover:underline text-sm font-medium"
          >
            Visit the Lab →
          </a>
        </article>
      </section>
    </div>
  </template>
  
  <script setup>
  // No script logic needed yet, but kept for future enhancements
  </script>
  