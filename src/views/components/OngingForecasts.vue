<template lang="pug">
  .section#ongoing
    .sticky
      .title Ongoing Forecasts
      //- tabs switch
      .forecasting-tabs
        .forecasting-tab-item(
          v-for="item in FORECAST_TABS"
          :key="item.value"
          :class="{'tab-active': item.value === activeTab}"
          @click="activeTab = item.value"
        ) {{item.label}}

    //- Samples
    .section-title.m-top-20 Forecasting Questions
    Filter.m-top-10(
      :show-forecast-country-filter="activeTab === 'macroeconomic'"
      :show-global-index-filter="activeTab === 'corporate'"
      v-bind="filterStates[activeTab]"
      show-type-filter
      @update="newState => handleUpdate(activeTab, newState)"
    )
    //- Corporate Samples
    el-table(v-show="activeTab === 'corporate'" :data="filteredCorporateData" border)
      el-table-column(label="ID" prop="taskId" width="100")
      el-table-column(label="Index" prop="index" max-width="100")
        template(#default="{row}")
          .img-wrap
            img(:src="getIndexImg(row.index)")
            span {{ row.index }}
      el-table-column(label="Company" prop="company")
      el-table-column(label="Question" prop="question")
      el-table-column(label="Forecast Type" prop="forecastType" width="150")
      el-table-column(label="Forecast End" prop="forecastEnd" width="130")
      el-table-column(label="Expected Answer Release Date" prop="expectedAnswerReleaseDate" width="180")
    //- Macroeconomic Samples
    el-table(v-show="activeTab === 'macroeconomic'" :data="filteredMacroData" border)
      el-table-column(label="ID" prop="taskId" width="100")
      el-table-column(label="Market" prop="market" width="100")
        template(#default="{row}")
          .img-wrap
            img(:src="getMarketImg(row.market)")
            span {{ row.market }}
      el-table-column(label="Question" prop="question")
      el-table-column(label="Forecast Type" prop="forecastType" width="150")
      el-table-column(label="Forecast End" prop="forecastEnd" width="130")
      el-table-column(label="Expected Answer Release Date" prop="expectedAnswerReleaseDate" width="180")
    .desc.m-top-10
      span If you would like to suggest a forecasting question, please submit it using this 
      a.link.link-green(href="https://forms.gle/9Np9Y3fDEDw8gzCY6" target="_blank") Google Form
      span . The OpenFinArena team will evaluate each suggestion and notify you if it is accepted.

    //- Scheduled Forecasts
    .section-title.m-top-20 Scheduled Forecasts
    el-table(:data="scheduledData" border)
      el-table-column(label="No." type="index" width="70")
      el-table-column(label="Method Name" prop="method")
      el-table-column(label="Method Type" prop="type")
      el-table-column(label="Organization" prop="organization")
        template(#default="{row}")
          .org
            img(:src="`/images/logo/${row.model}.svg`")
            span {{ row.organization }}
      el-table-column(label="Team" prop="team")
      el-table-column(label="Scheduled Forecast Date" prop="scheduledForecastDate")
    .desc.m-top-10
      span If you are willing to add your model to the scheduled forecasts, please submit the necessary information via the 
      a.link.link-green(href="https://forms.gle/SaRubQqeq9zzE1HPA" target="_blank") Google Form
      span .
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  onBeforeMount,
  onMounted,
  nextTick,
  computed
} from 'vue'
import { scheduledData } from '@/data/forecast'
import {
  FORECAST_TABS,
  GLOBAL_INDEX_TABS,
  FORECAST_COUNTRY_TABS
} from '@/data/constant'

interface ForecastItem {
  taskId: string
  index: string
  company?: string
  market?: string
  question: string
  forecastType: string
  forecastEnd: string
  expectedAnswerReleaseDate: string
}

const corporateData = ref<ForecastItem[]>([])
const macroData = ref<ForecastItem[]>([])
const activeTab = ref<'corporate' | 'macroeconomic'>('corporate')

const filterStates = reactive({
  corporate: {
    selectedIndex: 'overall',
    type: 'overall'
  },
  macroeconomic: {
    selectedCountry: 'overall',
    type: 'overall'
  }
})

const filteredCorporateData = computed<ForecastItem[]>(() => {
  let { selectedIndex, type } = filterStates.corporate
  selectedIndex = selectedIndex.toLowerCase()
  type = type.toLowerCase()

  const filtered = corporateData.value.filter(item => {
    const matchIndex =
      selectedIndex === 'overall' || item.index?.toLowerCase() === selectedIndex
    const matchType =
      type === 'overall' || item.forecastType?.toLowerCase() === type

    return matchIndex && matchType
  })

  if (selectedIndex === 'overall') {
    return filtered.sort(() => Math.random() - 0.5).slice(0, 10)
  }

  return filtered
})

const filteredMacroData = computed<ForecastItem[]>(() => {
  let { selectedCountry, type } = filterStates.macroeconomic
  selectedCountry = selectedCountry.toLowerCase()
  type = type.toLowerCase()

  const filtered = macroData.value.filter(item => {
    const matchIndex =
      selectedCountry === 'overall' ||
      item.market?.toLowerCase() === selectedCountry
    const matchType =
      type === 'overall' || item.forecastType?.toLowerCase() === type

    return matchIndex && matchType
  })

  if (selectedCountry === 'overall') {
    // 打乱顺序 （Fisher-Yates 洗牌算法）
    return filtered.sort(() => Math.random() - 0.5).slice(0, 10)
  }

  return filtered
})

onBeforeMount(() => {
  handleCorporateData()
  handleMacroData()
  handleScheduledData()
  window.removeEventListener('resize', handleResize)
})

onMounted(() => {
  nextTick(() => {
    getStickyTop()
    window.addEventListener('resize', handleResize)
  })
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

const handleCorporateData = async () => {
  const res = await fetch('/data/corporateSamples.json')
  if (!res.ok) throw new Error(`HTTP ${res.statusText}`)

  corporateData.value = await res.json()
}

const handleMacroData = async () => {
  const res = await fetch('/data/macroSamples.json')
  if (!res.ok) throw new Error(`HTTP ${res.statusText}`)

  macroData.value = await res.json()
}

const handleScheduledData = () => {
  const order: string[] = ['Thinking', 'Thinking + Search', 'Deep Research']
  scheduledData.sort((a, b) => order.indexOf(a.type) - order.indexOf(b.type))
}

const handleUpdate = (tab: 'corporate' | 'macroeconomic', newState: any) => {
  filterStates[tab] = { ...filterStates[tab], ...newState }
}

const getIndexImg = (index: string) => {
  const item = GLOBAL_INDEX_TABS.find(item =>
    index?.toLowerCase().includes(item.value)
  )
  return item?.src || ''
}
const getMarketImg = (market: string) => {
  const item = FORECAST_COUNTRY_TABS.find(item =>
    market?.toLowerCase().includes(item.value)
  )
  return item?.src || ''
}
</script>

<style lang="scss" scoped>
.sticky {
  position: sticky;
  top: var(--sticky-top, 100px);
  background: #f9f9fa;
  z-index: 999;
}

.img-wrap {
  display: flex;
  display: -webkit-flex;
  align-items: center;
  img {
    margin-right: 5px;
    width: 19px;
  }
}
</style>
