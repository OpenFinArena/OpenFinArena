import type { App } from 'vue'

// 手动导入要注册的组件
import Introduction from '@/components/Introduction.vue'
import Filter from '@/components/Filter.vue'
import LeaderboardChart from '@/components/LeaderboardChart.vue'
import LcharboardTable from '@/components/LeaderboardTable.vue'
import Links from '@/components/Links.vue'

export function registerGlobalComponents(app: App) {
  app.component('Introduction', Introduction)
  app.component('Filter', Filter)
  app.component('LeaderboardChart', LeaderboardChart)
  app.component('LeaderboardTable', LcharboardTable)
  app.component('Links', Links)
}