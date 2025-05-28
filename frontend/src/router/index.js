import { createRouter, createWebHistory } from 'vue-router';

import RepoGrid from '@/views/RepoGrid.vue';
import IssuesDashboard from '@/views/IssuesDashboard.vue';
import PullRequestDashboard from '@/views/PullRequestDashboard.vue';
// import more dashboards here...

const routes = [
  { path: '/', name: 'home', component: RepoGrid },
  {
    path: '/repos/:owner/:repo/issues',
    name: 'issues-dashboard',
    component: IssuesDashboard,
    props: true
  },
  {
    path: '/repos/:owner/:repo/pullRequests',
    name: 'pull-requests-dashboard',
    component: PullRequestDashboard,
    props: true
  }
  // add more dashboards here as needed
];

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
});
