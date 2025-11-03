<template lang="pug">
  Introduction
  Links
  .section
    .title Overall Leaderboard
    Filter(
      show-period-filter
      show-type-filter
      @update="overallLeaderboardUpdate"
    )
    LeaderboardChart(ref="chartRef" :scoreList="scoreList")
    LeaderboardTable(:scoreList="scoreList")
  .section
    .title Task
    .desc The task focuses on the forecast of corporate financial metrics or macroeconomic indicators. Formally, given a question 
      span.bold q 
      span that queries the state of the world at a future time, the objective is for a method 
      span.bold M 
      span to generate the answer 
      span.bold a 
      span to the question 
      span.bold q
      span .
    .desc.formula.italic a = M (q)
    .desc.m-top-20 For example, "What is the estimated year-over-year GDP growth rate for China in 2025?".
  OngingForecasts
  CompletedForecasts(:scoreList="scoreList")
  .section
    .title Participation
    .section-title.m-top-20 Forecasting Question Suggestion
    .desc
      span We welcome your contributions to our forecast queue in the FinDeepForecast Challenge. If you would like to suggest a forecasting question, please submit it using this 
      a.link.link-green(href="https://forms.gle/9Np9Y3fDEDw8gzCY6" target="_blank") Google Form
      span . The OpenFinArena team will evaluate each suggestion and notify you if it is accepted.
    .section-title.m-top-20 Service Registration or Prediction Submission
    .email.m-top-20 Online API Service Registration
    .desc
      span If you are willing to add your model to the scheduled forecasts, please submit the necessary information via the 
      a.link.link-green(href="https://forms.gle/SaRubQqeq9zzE1HPA" target="_blank") Google Form
      span .
    .email.m-top-20 Offline Prediction Submission
    .desc 
      span If you are interested in participating in the ongoing forecasts offline, please download the questions from 
      a.link.link-green(href="https://huggingface.co/datasets/OpenFinArena/FinDeepForecast" target="_blank") Hugging Face
      span . Once you complete the predictions locally, please send your results in 
      span.bold JSON format 
      span to 
      span.email OpenFinArena@gmail.com
      span .
    .desc.m-top-20
      span Example:
      pre
        code(ref="codeRef")
    .desc.m-top-20
      span Please use the following subject in your email: 
      span.bold FinDeepForecast-{Method Name}-{Method Type}-{Team Name}-{Organization}
      span .
    .desc.m-top-20
      span The 
      span.bold Method Name 
      span should be a unique name for your system/method, not just the name of the base model used (e.g., "MyAwesomeMethod", "FinAgent-v2", not "GPT-4").
    .desc.m-top-20
      span The 
      span.bold Method Type 
      span might be "Thinking", "Thinking + Search", "Deep Research" or other types that can best explain the type of your method.
    .desc.m-top-20
      span If the method type cannot be confirmed or you choose not to disclose it, please indicate "Other". If you have a dedicated logo for your Organization, please attach the logo in the size of 100x100, such as 
      img(src="/images/logo/chatgpt.svg" style="width:25px; height:25px; margin-left:5px; margin-right:5px")
      span for OpenAI, which will be presented in the leaderboard.
</template>

<script setup lang="ts">
import OngingForecasts from './components/OngingForecasts.vue'
import CompletedForecasts from './components/CompletedForecasts.vue'
import Submission from '@/components/Submission.vue'
import {
  ref,
  nextTick,
  onBeforeMount,
  onMounted,
  type ComponentPublicInstance
} from 'vue'
import { countryList } from '@/types'
import { samplesData, scoreData } from '@/data/deepResearch.ts'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css' // 深色主题

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

const completedTab = ref<string>('corporate')
const tabOptions = [
  {
    label: 'Corporate Financial Forecasting',
    value: 'corporate'
  },
  {
    label: 'Macroeconomic Indicator Forecasting',
    value: 'macroeconomic'
  }
]

const codeRef = ref<HTMLElement | null>(null)
const exampleJson = ref([
  { id: '1233', prediction: '23.4' },
  { id: '4561', prediction: '4.5%' }
])

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

onMounted(() => {
  nextTick(() => {
    if (codeRef.value) {
      // 格式化数组对象（缩进 2 空格，保留结构）
      codeRef.value.textContent = JSON.stringify(exampleJson.value, null, 2)
      // 高亮 JSON 语法
      hljs.highlightElement(codeRef.value)
    }
  })
})

const overallLeaderboardUpdate = (filters: any) => {
  // console.log('filters', filters)
}

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

async function countryChange(countryCode: string) {
  activeCountry.value = countryCode
  handleScoreList()
  await nextTick()
  chartRef?.value?.renderChart()
}
</script>

<style lang="scss" scoped>
#ongoing,
#completed {
  scroll-margin-top: var(--scroll-margin, 0px);
}

:deep .forecasting-tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 10px;
  background: #ffffff;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  line-height: 32px;
  color: #a6a6a6;
  font-size: 24px;
  padding: 0 5px;

  .forecasting-tab-item {
    margin: 5px 0;
    padding: 10px;
    text-align: center;
    width: 50%;
    cursor: pointer;
  }

  .tab-active {
    border-radius: 10px;
    background: #e8a107;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
    color: #fff;
  }
}
</style>
