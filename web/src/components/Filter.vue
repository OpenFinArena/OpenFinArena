<template lang="pug">
  .filter-wrap
    //- Country Tabs for FinDocResearch & FinDeepResearch
    .filter-list(v-if="showDocDeepCountryFilter")
      .filter-item(
        v-for="item in DOC_DEEP_COUNTRY_TAB"
        :key="item.value"
        :class="{'active-yellow': item.value === selectedDocDeepCountry}"
        @click="selectedDocDeepCountry = item.value"
      )
        img(v-if="item.src" :src="item.src")
        span {{ item.label }}

    //- Perild Tabs
    .filter-list(v-if="showPeriodFilter")
      .filter-item(
        v-for="item in PERIOD_TABS"
        :key="item.value"
        :class="{'active-yellow': item.value === selectedPeriod}"
        @click="periodChange(item.value)"
      ) 
        img(v-if="item.src" :src="item.src")
        span {{ item.label }}
      el-date-picker(
        v-if="selectedPeriod && selectedPeriod !== 'quarterly' && selectedPeriod !== 'overall'"
        v-model="selectedTime"
        :type="pickerType"
        :format="pickerFormat"
        :value-format="pickerValueFormat"
        :placeholder="`Select ${selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1)}`"
        style="margin-left: 24px;"
      )
      el-select(v-if="selectedPeriod === 'quarterly'" v-model="selectedTime" placeholder="Select Quarter")
        el-option(
          v-for="item in QUARTER_OPTIONS"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        )

    //- Market Tabs
    .filter-list(v-if="showMarketFilter")
      .filter-item(
        v-for="item in MARKET_TABS"
        :key="item.value"
        :class="{'active-blue': item.value === selectedMarket}"
        @click="selectedMarket = item.value"
      )
        img(v-if="item.src" :src="item.src")
        span {{ item.label }}

    //- Forecast Country Tabs
    .filter-list(v-if="showForecastCountryFilter")
      .filter-item(@click="selectedForecastCountry = 'overall'" :class="{'active-blue':  selectedForecastCountry === 'overall'}")
        AllIcon
        span All
      .filter-item(
        v-for="item in FORECAST_COUNTRY_TABS"
        :key="item.value"
        :class="{'active-blue': item.value === selectedForecastCountry}"
        @click="selectedForecastCountry = item.value"
      )
        img(v-if="item.src" :src="item.src")
        span {{ item.label }}

    //- Global Index Tabs
    .filter-list(v-if="showGlobalIndexFilter")
      .filter-item(@click="selectedGlobalIndex = 'overall'" :class="{'active-blue':  selectedGlobalIndex === 'overall'}")
        AllIcon
        span All
      .filter-item(
        v-for="item in GLOBAL_INDEX_TABS"
        :key="item.value"
        :class="{'active-blue': item.value === selectedGlobalIndex}"
        @click="selectedGlobalIndex = item.value"
      )
        img(v-if="item.src" :src="item.src")
        span {{ item.label }}
    
    //- Type Tabs
    .filter-list(v-if="showTypeFilter")
      .filter-item(@click="selectedType = 'overall'" :class="{'active-green':  selectedType === 'overall'}")
        AllIcon
        span All
      .filter-item(
        v-for="item in TYPE_TABS"
        :key="item.value"
        :class="{'active-green': item.value === selectedType}"
        @click="selectedType = item.value"
      ) {{ item.label }}
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import AllIcon from '@/assets/icons/all.svg'
import {
  DOC_DEEP_COUNTRY_TAB,
  PERIOD_TABS,
  QUARTER_OPTIONS,
  FORECAST_COUNTRY_TABS,
  GLOBAL_INDEX_TABS,
  TYPE_TABS
} from '@/data/constant'

interface Props {
  showDocDeepCountryFilter?: boolean
  showPeriodFilter?: boolean
  showMarketFilter?: boolean
  showTypeFilter?: boolean
  showForecastCountryFilter?: boolean
  showGlobalIndexFilter?: boolean
  selectedIndex?: string
  selectedCountry?: string
  type?: string
  period?: string
  time?: any
}

const props = withDefaults(defineProps<Props>(), {
  showDocDeepCountryFilter: false,
  showPeriodFilter: false,
  showMarketFilter: false,
  showTypeFilter: false,
  showForecastCountryFilter: false,
  showGlobalIndexFilter: false,
  selectedCountry: 'overall',
  selectedIndex: 'overall',
  type: 'overall',
  period: 'overall',
  time: ''
})

// 筛选状态
const selectedDocDeepCountry = ref<string>('overall')
const selectedPeriod = ref(props.period)
const selectedTime = ref(props.time)
const selectedMarket = ref<string>('overall')
const selectedForecastCountry = ref(props.selectedCountry)
const selectedGlobalIndex = ref(props.selectedIndex)
const selectedType = ref(props.type)

const pickerType = computed<string>(() => {
  switch (selectedPeriod.value) {
    case 'weekly':
      return 'week'
    case 'monthly':
      return 'month'
    case 'yearly':
      return 'year'
    default:
      return 'month'
  }
})
const pickerFormat = computed<string>(() => {
  switch (selectedPeriod.value) {
    case 'weekly':
      return 'YYYY [Week] ww'
    case 'monthly':
      return 'YYYY-MM'
    case 'yearly':
      return 'YYYY'
    default:
      return 'YYYY-MM'
  }
})
const pickerValueFormat = computed<string>(() => {
  switch (selectedPeriod.value) {
    case 'weekly':
      return 'YYYY-[W]ww'
    case 'monthly':
      return 'YYYY-MM'
    case 'yearly':
      return 'YYYY'
    default:
      return 'YYYY-MM'
  }
})

const emit = defineEmits<{
  (
    e: 'update',
    payload: {
      docDeepCountry: string
      period: string
      time: string
      market: string
      type: string
      selectedCountry: string
      selectedIndex: string
    }
  ): void
}>()

const activeFilters = computed(() => {
  let time = selectedTime.value

  if (selectedPeriod.value === 'overall') {
    time = 'overall'
  }
  // }else {
  // if (selectedTime.value) {
  //   time = selectedTime.value
  // } else {
  //   return {
  //     docDeepCountry: '',
  //     period: '',
  //     time: '',
  //     market: '',
  //     type: '',
  //     selectedCountry: '',
  //     selectedIndex: ''
  //   }
  // }
  // }

  return {
    docDeepCountry: props.showDocDeepCountryFilter
      ? selectedDocDeepCountry.value
      : '',
    period: props.showPeriodFilter ? selectedPeriod.value : '',
    time: props.showPeriodFilter ? time : '',
    market: props.showMarketFilter ? selectedMarket.value : '',
    type: props.showTypeFilter ? selectedType.value : '',
    selectedCountry: props.showForecastCountryFilter
      ? selectedForecastCountry.value
      : '',
    selectedIndex: props.showGlobalIndexFilter ? selectedGlobalIndex.value : ''
  }
})

watch(
  [
    selectedDocDeepCountry,
    selectedPeriod,
    selectedTime,
    selectedMarket,
    selectedType,
    selectedForecastCountry,
    selectedGlobalIndex
  ],
  () => {
    emit('update', { ...activeFilters.value })
  },
  { deep: true, immediate: true }
)

watch(
  () => props,
  newProps => {
    if (newProps.period) {
      selectedPeriod.value = newProps.period
    }
    if (newProps.time) {
      selectedTime.value = newProps.time
    }
    if (newProps.selectedCountry) {
      selectedForecastCountry.value = newProps.selectedCountry
    }
    if (newProps.selectedIndex) {
      selectedGlobalIndex.value = newProps.selectedIndex
    }
    if (newProps.type) {
      selectedType.value = newProps.type
    }
  },
  { deep: true }
)

const periodChange = (value: string) => {
  if (value !== selectedPeriod.value) {
    selectedPeriod.value = value
    selectedTime.value = ''
  }
}
</script>

<style scoped lang="scss">
img,
svg {
  margin-right: 5px;
  width: 19px;
}

.el-select {
  margin-left: 24px;
  width: 220px;
}
</style>
