<template lang="pug">
  .section#completed
    .sticky
      .title Completed Forecasts
      //- tabs switch
      .forecasting-tabs
        .forecasting-tab-item(
          v-for="item in FORECAST_TABS"
          :key="item.value"
          :class="{'tab-active': item.value === activeTab}"
          @click="activeTab = item.value"
        ) {{item.label}}

    //- Leaderboard
    .section-title.m-top-10 Leaderboard
    Filter.m-top-10(
      :show-forecast-country-filter="activeTab === 'macroeconomic'"
      :show-global-index-filter="activeTab === 'corporate'"
      show-period-filter
      show-type-filter
      v-bind="filterLeaderboardStates[activeTab]"
      @update="newState => handleLeaderboardFilterUpdate(activeTab, newState)"
    )
    LeaderboardChart(ref="chartRef" :scoreList="scoreList")
    LeaderboardTable(:scoreList="scoreList")

    //- Samples
    template(v-if="false")
      .section-title.m-top-20 Samples
      Filter(
        :show-forecast-country-filter="activeTab === 'macroeconomic'"
        :show-global-index-filter="activeTab === 'corporate'"
        show-period-filter
        show-type-filter
        v-bind="filterSampleStates[activeTab]"
        @update="newState => handleSampleFilterUpdate(activeTab, newState)"
      )
      el-table(v-show="activeTab === 'corporate'" :data="corporateSamplesData" border)
        el-table-column(label="ID" prop="id")
        el-table-column(label="Index" prop="index")
        el-table-column(label="Company" prop="company")
        el-table-column(label="Question" prop="question")
        el-table-column(label="Reference Answer" prop="referenceAnswer")
        el-table-column(label="Forecast Type" prop="forecastType")
        el-table-column(label="Forecast End" prop="forecastEnd")
        el-table-column(label="Answer Release Date" prop="answerReleaseDate")
      el-table(v-show="activeTab === 'macroeconomic'" :data="macroSamplesData" border)
        el-table-column(label="ID" prop="id")
        el-table-column(label="Market" prop="market")
        el-table-column(label="Question" prop="question")
        el-table-column(label="Reference Answer" prop="referenceAnswer")
        el-table-column(label="Forecast Type" prop="forecastType")
        el-table-column(label="Forecast End" prop="forecastEnd")
        el-table-column(label="Answer Release Date" prop="answerReleaseDate")
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  onMounted,
  onBeforeUnmount,
  type ComponentPublicInstance,
  nextTick
} from 'vue'
import { FORECAST_TABS } from '@/data/constant'

interface ScoreItem {
  [key: string]: any
}
const props = withDefaults(
  defineProps<{
    scoreList: ScoreItem[]
  }>(),
  {
    scoreList: () => []
  }
)
const chartRef = ref<ComponentPublicInstance<{
  renderChart: () => void
}> | null>(null)
const activeTab = ref<'corporate' | 'macroeconomic'>('corporate')

const filterSampleStates = reactive({
  corporate: {
    period: 'overall',
    time: '',
    selectedIndex: 'overall',
    type: 'overall'
  },
  macroeconomic: {
    period: 'overall',
    time: '',
    selectedCountry: 'overall',
    type: 'overall'
  }
})
const filterLeaderboardStates = reactive({
  corporate: {
    period: 'overall',
    time: '',
    selectedIndex: 'overall',
    type: 'overall'
  },
  macroeconomic: {
    period: 'overall',
    time: '',
    selectedCountry: 'overall',
    type: 'overall'
  }
})

const corporateSamplesData = [
  {
    id: 1,
    index: 'Nasdaq 100',
    company: 'Tesla',
    question: 'What’s the estimated total revenue in 2025 Q3?',
    referenceAnswer: 'Estimated total revenue is 2%.',
    forecastType: 'Recurrent',
    forecastEnd: '2025-09-30',
    answerReleaseDate: '2025-10-21'
  },
  {
    id: 2,
    index: 'Nasdaq 100',
    company: 'Tesla',
    question: 'What is the recent performance trend of the NASDAQ-100?',
    referenceAnswer: 'The recent performance trend is 2%.',
    forecastType: 'Situational',
    forecastEnd: '2025-09-30',
    answerReleaseDate: '2025-10-21'
  }
]

const macroSamplesData = [
  {
    id: 1,
    market: 'US',
    flag: '🇺🇸',
    question:
      'What’s the estimated highest interest rate of the US in Oct 2025?',
    referenceAnswer: 'The recent performance trend is 2%.',
    forecastType: 'Recurrent',
    forecastEnd: '2025-09-30',
    answerReleaseDate: '2025-11-01'
  },
  {
    id: 2,
    market: 'US',
    flag: '🇺🇸',
    question:
      'What’s the estimated highest interest rate of the US in Oct 2025?',
    referenceAnswer: 'The recent performance trend is 2%.',
    forecastType: 'Situational',
    forecastEnd: '2025-09-30',
    answerReleaseDate: '2025-11-01'
  }
]

const scheduledData = [
  {
    no: 1,
    methodName: 'GPT-5',
    methodType: 'Thinking',
    organization: 'OpenAI',
    team: 'Official',
    scheduledForecastDate: '2025-10-25'
  },
  {
    no: 2,
    methodName: 'PIKE-Report',
    methodType: 'Thinking + Search',
    organization: 'Microsoft Research Asia',
    team: 'Token Fund',
    scheduledForecastDate: '2025-10-25'
  },
  {
    no: 3,
    methodName: 'Gemini 2.5 Pro',
    methodType: 'Search',
    organization: 'Google',
    team: 'Token Fund',
    scheduledForecastDate: '2025-10-25'
  }
]

onMounted(() => {
  nextTick(() => {
    getStickyTop()
    window.addEventListener('resize', handleResize)
  })
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  getStickyTop()
}
const getStickyTop = () => {
  const header = document.querySelector('.header')
  const headerHeight = header?.clientHeight || 0
  document.documentElement.style.setProperty(
    '--sticky-top',
    `${headerHeight}px`
  )
}
const handleSampleFilterUpdate = (
  tab: 'corporate' | 'macroeconomic',
  newState: any
) => {
  filterSampleStates[tab] = { ...filterSampleStates[tab], ...newState }
}
const handleLeaderboardFilterUpdate = (
  tab: 'corporate' | 'macroeconomic',
  newState: any
) => {
  // console.log(newState)
  filterLeaderboardStates[tab] = {
    ...filterLeaderboardStates[tab],
    ...newState
  }
}
</script>

<style lang="scss" scoped>
.sticky {
  position: sticky;
  top: var(--sticky-top, 100px);
  background: #f9f9fa;
  z-index: 999;
}
</style>
