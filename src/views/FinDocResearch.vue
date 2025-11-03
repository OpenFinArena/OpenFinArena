<template lang="pug">
  Introduction
  Links
  .section
    .title Leaderboard
        Filter(show-doc-deep-country-filter @update="countryChange")
    .chart-wrapper
      .chart(ref="chartRef")
    el-table.m-top-20(:data="scoreList" border)
      el-table-column(label="Rank" width="100" align="center")
        template(#default="scope")
          .rank
            span.medal.gold(v-if="scope.$index === 0") {{scope.$index + 1 }}
            span.medal.silver(v-else-if="scope.$index === 1") {{scope.$index + 1 }}
            span.medal.copper(v-else-if="scope.$index === 2") {{scope.$index + 1 }}
            span(v-else) {{scope.$index + 1 }}
      el-table-column(prop="method" label="Method Name")
      el-table-column(prop="organization" label="Organization")
        template(#default="{row}")
          .org
            template(v-if="row.model")
              img(v-if="row.imageType == 'jpg'" :src="`/images/logo/${row.model}.jpg`")
              img(v-else-if="row.imageType == 'png'" :src="`/images/logo/${row.model}.png`")
              img(v-else :src="`/images/logo/${row.model}.svg`")
            span {{ row.organization }}
      el-table-column(prop="score" label="Score")
        template(#default="{row}")
          span.bold {{ row.score ? Number(row.score).toFixed(1) : '--' }}
      el-table-column(prop="team" label="Team")
      el-table-column(prop="submittedDate" label="Submitted Date")
  .section
    .title Task
    .desc FinDocResearch requires methods to generate a rigorous, structured research report based solely on a pair of multi-year annual reports of a listed company. The use of external data sources other than the provided annual reports, such as websites, news articles, and financial data providers, is strictly prohibited.
    .desc.m-top-20
      span Formally, given two annual reports 
      span.bold.italic (d1, d2) 
      span of a listed company and a desired report structure 
      span.bold.italic S
      span , a method 
      span.bold.italic M 
      span is required to produce a research report 
      span.bold.italic R 
      span strictly following the report structure 
      span.bold.italic 𝑆
      span .
    .desc.formula.italic R = M (d1, d2, 𝑆)
  .section
    .title Desired Report Structure
    .subtitle The desired structure of the research report:
    ul.p-left-40
      li.subtitle
        span Company Overview
        span : This section provides a concise overview of the company, including:
        ul.p-left-40
          li Basic Information
          li Core Competencies
          li Mission & Vision
      li.subtitle
        span Financial Performance
        span : This section presents a detailed analysis of the company’s financial health, including:
        ul.p-left-40
          li Income Statement
          li Balance Sheet
          li Cash Flow Statement
          li Key Financial Ratios
          li Operating Performance
      li.subtitle
        span Business Analysis
        span : This section provides a summary and analysis of a company’s business performance and strategies, including:
        ul.p-left-40
          li Profitability Analysis
          li Financial Performance Summary
          li Business Competitiveness
      li.subtitle
        span Risk Factors
        span : This section identifies and discusses the principal risks the company faces, including:
        ul.p-left-40
          li Market Risks
          li Operational Risks
          li Financial Risks
          li Compliance Risks
      li.subtitle
        span Corporate Governance
        span : This section outlines the company’s governance framework, including:
        ul.p-left-40
          li Board Composition
          li Internal Controls
      li.subtitle
        span Future Outlook
        span : This section provides management’s projections and strategic plans for the future, including:
        ul.p-left-40
          li Strategic Direction
          li Challenges and Uncertainties
          li Innovation and Development Plans
    .desc
      span For a more detailed overview of the structure, please refer to this 
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDocResearch" target="_blank") link
      span .
  .section
    .title Samples
    el-table(:data="samplesData" border)
      el-table-column(prop="market", label="Market", width="100")
        template(#default="{row}")
          .market
            img(:src="getCountrySrc(row.market)")
            span.country {{ row.market }}
      el-table-column(prop="companyName", label="Company Name")
      el-table-column(prop="inputAnnualReports", label="Input Annual Reports")
        template(#default="{row}")
          div(v-for="file in row.inputAnnualReports" :key="file") {{file}}
      el-table-column(prop="sampleOutputReport", label="Sample Output Report")
    .desc.m-top-20
      span The above input annual reports and the corresponding sample output reports in FinDocResearch can be downloaded via the 
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDocResearch" target="_blank") link
  .section
    .title Dataset
    .subtitle Selected listed companies and annual reports:
    ul.p-left-40
      li.subtitle
        span 4 Languages
        span : English, Simplified Chinese, Traditional Chinese and Indonesian Bahasa
      li.subtitle
        span 8 Markets
        span : United States (US), United Kingdom (UK), China(CN), Hong Kong (HK), Australia (AU), Singapore (SG), Malaysia (MY) and Indonesia (ID)
      li.subtitle
        span 10 Industries (BICS)
        span : Communications, Consumer Discretionary, Consumer Staples, Energy, Health Care, Industrials, Materials, Real Estate,Technology, and Utilities, etc.
      li.subtitle
        span 80 Companies
        span : 10 companies from each market
      li.subtitle
        span 160 reports
        span : 2 annual reports (i.e., 2023 and 2024) for each selected company are provided
    el-table.m-top-20(:data="dataset" border)
      el-table-column(prop="market" label="Market")
        template(#default="{row}")
          .market
            img(:src="getCountrySrc(row.market)")
            span.country {{ row.market }}
      el-table-column(prop="companyCount" label="No. of Companies")
      el-table-column(prop="documentCount" label="No. of Documents")
      el-table-column(prop="maxPageCount" label="Max No. of Pages per Document")
      el-table-column(prop="minPageCount" label="Min No. of Pages per Document")
      el-table-column(prop="avgPageCount" label="Average No. of Pages per Document")
      el-table-column(prop="examples" label="Examples")
        template(#default="{row}")
          span {{row.examples.join(', ')}}
    .desc.m-top-20
      span The whole FinDocResearch dataset for evaluation can be downloaded via the  
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDocResearch" target="_blank") link
      span .
  Submission(emailTitle="FinDocResearch-{Method Name}-{Team Name}-{Organization}")

</template>

<script setup lang="ts">
import Submission from '@/components/Submission.vue'
import {
  ref,
  onBeforeMount,
  onMounted,
  onBeforeUnmount,
  nextTick,
  type ComponentPublicInstance
} from 'vue'
import { countryList } from '@/types'
import { scoreData, samplesData, dataset } from '@/data/docResearch.ts'
import * as echarts from 'echarts'

interface ModelScore {
  name: string
  score: number
}

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

// 图表实例
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

// 当前选择的国家
const activeCountry = ref<string>('overall')
// 分数列表
const scoreList = ref<ScoreItem[]>([])

onBeforeMount(() => {
  handleScoreList()
})

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    renderChart()
    window.addEventListener('resize', handleResize)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})

function handleResize() {
  chart?.resize()
}

function getCountrySrc(countryCode: string): string {
  const country = countryList.find(c => c.label === countryCode)
  return country ? country.src : ''
}

function handleScoreList() {
  scoreList.value = scoreData
    .filter(item => item.method !== 'SilverSight Agent')
    .map((item: any) => ({
      method: item.method,
      organization: item.organization,
      team: item.team,
      submittedDate: item.submittedDate,
      model: item.model,
      score: getScore(item),
      imageType: item.imageType
    }))

  scoreList.value.sort((a, b) => {
    return b.score - a.score
  })
}

async function countryChange(filters: any) {
  activeCountry.value = filters.docDeepCountry
  handleScoreList()
  await nextTick()
  renderChart()
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

function renderChart() {
  if (!chart) return

  const option: echarts.EChartsOption = {
    backgroundColor: '#fff',
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: scoreList.value.map(d => d.method),
      axisLabel: { rotate: 25, color: '#666', fontSize: 12 },
      axisLine: { lineStyle: { color: '#ccc' } }
    },
    yAxis: {
      type: 'value',
      name: 'Score',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: { color: '#888', fontSize: 12 },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}'
    },
    series: [
      {
        type: 'bar',
        data: scoreList.value.map(d => d.score),
        itemStyle: {
          color: '#60ABFE'
        },
        label: {
          show: true,
          position: 'insideTop',
          color: '#333',
          fontWeight: 'bold',
          formatter: '{c}'
        }
      },
      {
        type: 'scatter',
        data: scoreList.value.map((item, index) => {
          return {
            name: item.method,
            value: item.score,
            symbol: `image://${getImageSrc(item)}`,
            symbolSize: [24, 24]
          }
        }),
        symbolOffset: [0, -25],
        silent: true,
        tooltip: { show: false },
        z: 120
      }
    ]
  }

  chart.setOption(option)
}

const getImageSrc = (item: any) => {
  switch (item.imageType) {
    case 'png':
      return `/images/logo/${item.model}.png`
    case 'jpg':
      return `/images/logo/${item.model}.jpg`
    default:
      return `/images/logo/${item.model}.svg`
  }
}
</script>

<style lang="scss" scoped>
.country-list {
  img {
    margin-right: 10px;
    width: 19px;
  }
}

.chart {
  width: 100%;
  height: 400px;
}
</style>
