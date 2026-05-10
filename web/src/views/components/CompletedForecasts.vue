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
          @click="tabSwitch(item.value)"
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
    template(v-if="showLeaderboard" )
      LeaderboardChart(ref="chartRef" :scoreList="activeTab === 'corporate' ? filteredCorporateData : filteredMacroData")
      LeaderboardTable(:scoreList="activeTab === 'corporate' ? filteredCorporateData : filteredMacroData")

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
  onBeforeMount,
  onMounted,
  onBeforeUnmount,
  type ComponentPublicInstance,
  nextTick,
  computed
} from 'vue'
import { FORECAST_TABS } from '@/data/constant'
import { useWeekInfo } from '@/plugins/useWeekInfo'

interface ScoreItem {
  [key: string]: any
}

const corporateData = ref<ScoreItem[]>([])
const macroData = ref<ScoreItem[]>([])

const chartRef = ref<ComponentPublicInstance<{
  renderChart: () => void
}> | null>(null)
const activeTab = ref<'corporate' | 'macroeconomic'>('corporate')
const showLeaderboard = ref(false)

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

const filteredCorporateData = computed<ScoreItem[]>(() => {
  let { period, time, selectedIndex, type } = filterLeaderboardStates.corporate
  selectedIndex = selectedIndex.toLowerCase().replace(' ', '')
  type = type.toLowerCase()

  const filtered = corporateData.value.filter(item => {
    let matchTime = true

    const matchType =
      type === 'overall' || item.forecastType?.toLowerCase() === type

    if (period === 'weekly' && time) {
      matchTime = item.week === time
    } else if (period === 'monthly' && time) {
      const { months } = useWeekInfo(item.week)
      matchTime = months.includes(time)
    }

    if (matchTime && matchType) {
      item.score = item[selectedIndex]
      return true
    }

    return false
  })

  return filtered
})

const filteredMacroData = computed<ScoreItem[]>(() => {
  let { period, time, selectedCountry, type } =
    filterLeaderboardStates.macroeconomic
  selectedCountry = selectedCountry.toLowerCase().replace(' ', '')
  type = type.toLowerCase()

  const filtered = macroData.value.filter(item => {
    let matchTime = true

    const matchType =
      type === 'overall' || item.forecastType?.toLowerCase() === type

    if (period === 'weekly' && time) {
      matchTime = item.week === time
    } else if (period === 'monthly' && time) {
      const { months } = useWeekInfo(item.week)
      matchTime = months.includes(time)
    }

    if (matchTime && matchType) {
      item.score = item[selectedCountry]
      return true
    }

    return false
  })

  return filtered
})

onBeforeMount(async () => {
  await handleCorporateData()
  await handleMacroData()
  showLeaderboard.value = true
})

onMounted(() => {
  nextTick(() => {
    getStickyTop()
    window.addEventListener('resize', handleResize)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const handleCorporateData = async () => {
  const res = await fetch('/data/corporateLeaderboard.json')
  if (!res.ok) throw new Error(`HTTP ${res.statusText}`)

  corporateData.value = await res.json()
}

const handleMacroData = async () => {
  const res = await fetch('/data/macroLeaderboard.json')
  if (!res.ok) throw new Error(`HTTP ${res.statusText}`)

  macroData.value = await res.json()
}

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

const handleLeaderboardFilterUpdate = async (
  tab: 'corporate' | 'macroeconomic',
  newState: any
) => {
  filterLeaderboardStates[tab] = {
    ...filterLeaderboardStates[tab],
    ...newState
  }

  await nextTick()
  chartRef?.value?.renderChart()
}

const tabSwitch = async (tab: 'corporate' | 'macroeconomic') => {
  activeTab.value = tab
  await nextTick()
  chartRef?.value?.renderChart()
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
