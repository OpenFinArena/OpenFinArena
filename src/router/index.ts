import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Overview from '@/views/Overview.vue'
import FinDocResearch from '@/views/FinDocResearch.vue'
import FinDeepResearch from '@/views/FinDeepResearch.vue'
import FinDeepForecast from '@/views/FinDeepForecast.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/',
      component: HomeView,
      children: [
        {
          path: '/',
          name: 'overview',
          component: Overview,
          meta: {
            title: 'Overview',
          },
        },
        {
          path: '/fin-doc-research',
          name: 'fin-doc-research',
          component: FinDocResearch,
          meta: {
            title: 'FinDocResearch',
          },
        },
        {
          path: '/fin-deep-research',
          name: 'fin-deep-research',
          component: FinDeepResearch,
          meta: {
            title: 'FinDeepResearch',
          },
        },
        {
          path: '/fin-deep-forecast',
          name: 'fin-deep-forecast',
          component: FinDeepForecast,
          meta: {
            title: 'FinDeepForecast',
          },
        },
      ],
    }
  ],
})

export default router
