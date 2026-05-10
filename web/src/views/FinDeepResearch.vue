<template lang="pug">
  Introduction
  Links
  .section
    .title Leaderboard
    Filter(show-doc-deep-country-filter @update="countryChange")
    LeaderboardChart(ref="chartRef" :scoreList="scoreList")
    LeaderboardTable(:scoreList="scoreList")
  .section
    .title Task
    .desc The task aims to generate a comprehensive research report for a listed company by adhering to an expert-designed analytical framework and synthesizing heterogeneous financial data from diverse web sources, including corporate disclosures, financial news, stock prices, and market indices.
    .desc.m-top-20
      span Formally, given a research task instruction 
      span.bold.italic 𝑖 &nbsp;
      span with a desired analytical structure 
      span.bold.italic S
      span , a method 
      span.bold.italic M 
      span is required to produce a research report 
      span.bold.italic R 
      span strictly following the analytical structure 
      span.bold.italic 𝑆
      span .
    .desc.formula.italic R = M (𝑖, 𝑆)
    img.formula-img.m-top-20(src="/images/formula.png")
  .section
    .title Samples
    el-table(:data="samplesData" border)
      el-table-column(prop="market" label="Market" )
        template(#default="{row}")
          .market
            img(:src="getCountrySrc(row.market)")
            span.country {{ row.market }}
      el-table-column(prop="companyName", label="Company Name")
      el-table-column(prop="inputAnalyticalStructure", label="Input Analytical Structure")
      el-table-column(prop="sampleOutputReport", label="Sample Output Report")
    .desc.m-top-20
      span For more details about the the above samples, please refer to the 
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDeepResearch" target="_blank") analytical structure 
      span &nbsp;and 
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDeepResearch" target="_blank") sample output report
      span .
  .section
    .title Dataset
    .subtitle Selected companies:
    ul.p-left-40
      li.subtitle
        span 4 Languages
        span : English, Simplified Chinese, Traditional Chinese and Indonesian Bahasa
      li.subtitle
        span 8 Markets
        span : United States (US), United Kingdom (UK), China(CN), Hong Kong (HK), Australia (AU), Singapore (SG), Malaysia (MY) and Indonesia (ID)
      li.subtitle
        span 10 Industries (BICS)
        span : Communications, Consumer Discretionary, Consumer Staples, Energy, Health Care, Industrials, Materials, Real Estate,Technology, and Utilities
      li.subtitle
        span 64 Companies
        span : 8 companies from each market
    .desc.m-top-20
      span The whole FinDeepResearch dataset for evaluation can be downloaded via the 
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDeepResearch" target="_blank") link
      span .
  Submission(emailTitle="FinDeepResearch-{Method Name}-{Method Type}-{Team Name}-{Organization}" show-method-type)
</template>

<script setup lang="ts">
import Submission from '@/components/Submission.vue'
import { ref, nextTick, onBeforeMount, type ComponentPublicInstance } from 'vue'
import { countryList } from '@/types'
import { samplesData, scoreData } from '@/data/deepResearch.ts'

interface ScoreItem {
  [key: string]: any
}

interface CountryScores {
  us: number
  uk: number
  cn: number
  hk: number
  au: number
  sg: number
  my: number
  ind: number
  [key: string]: number | undefined
}

const chartRef = ref<ComponentPublicInstance<{
  renderChart: () => void
}> | null>(null)
// 当前选择的国家
const activeCountry = ref<string>('overall')
// 分数列表
const scoreList = ref<ScoreItem[]>([])

onBeforeMount(() => {
  handleScoreList()
})

function handleScoreList() {
  scoreList.value = scoreData.map((item: any) => ({
    method: item.method,
    type: item.type,
    organization: item.organization,
    team: item.team,
    submittedDate: item.submittedDate,
    model: item.model,
    score: getScore(item)
  }))

  scoreList.value.sort((a, b) => {
    return b.score - a.score
  })
}

function getScore(socreItem: CountryScores): number | string | undefined {
  if (activeCountry.value === 'overall') {
    return (
      (socreItem.us +
        socreItem.uk +
        socreItem.cn +
        socreItem.hk +
        socreItem.au +
        socreItem.sg +
        socreItem.my +
        socreItem.ind) /
      8
    ).toFixed(1)
  } else {
    return (socreItem as any)[activeCountry.value]
  }
}

function getCountrySrc(countryCode: string): string {
  const country = countryList.find(c => c.label === countryCode)
  return country ? country.src : ''
}

async function countryChange(filters: any) {
  activeCountry.value = filters.docDeepCountry
  handleScoreList()
  await nextTick()
  chartRef?.value?.renderChart()
}
</script>

<style lang="scss" scoped>
.formula-img {
  width: 100%;
  border-radius: 12px;
}
</style>
