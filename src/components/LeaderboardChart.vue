<template lang="pug">
  .chart-wrapper
    .chart(ref="chartRef")
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts';

interface ScoreItem {
  [key: string]: any
}

const props = defineProps<{
  scoreList: ScoreItem[]
}>()

// 图表实例
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

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

const handleResize = () => {
  chart?.resize()
}

// 转换函数：安全转换为数字，没值就为0
const toNum = (val: unknown): number => (val === undefined || val === null || val === '' ? 0 : Number(val) || 0);

function renderChart() {
  if (!chart) return;

  const legend = [{ label: 'LLM (Thinking)', value: 'Thinking' }, { label: 'LLM (Thinking + Search)', value: 'Thinking + Search' }, { label: 'Deep Research', value: 'Deep Research' }]
  const categoryData = [...new Set(props.scoreList.map((item: ScoreItem) => item.method))] as string[];
  const colors = ['#26C6DA', '#FFB74D', '#64B5F6']
  const seriesData = categoryData.map(category => {
    const data: { [key: string]: number | string } = {}

    const methodList = props.scoreList.filter((item: ScoreItem) => item.method === category)
    methodList.forEach((item: ScoreItem) => {
      data.method = item.method
      data[item.type] = item.score
      data.src = `/images/logo/${item.model}.svg`
    })

    return data
  })

  const dataGroups = seriesData.map(item => [
    toNum(item['Thinking']) ?? 0,
    toNum(item['Thinking + Search']) ?? 0,
    toNum(item['Deep Research']) ?? 0,
  ])

  // 计算每组最大值（用于确定柱子顶端位置）
  const maxValues = dataGroups.map(group => Math.max(...group))

  // 归一化处理（让堆叠总高度等于最大值）
  const normalizedData = dataGroups.map((group, index) => {
    const sum = group.reduce((acc, val) => acc + val, 0);
    const max = maxValues[index] ?? 0;
    const ratio = sum > 0 ? max / sum : 1
    return group.map(val => val * ratio)
  })

  // 构建系列化数据（堆叠柱）
  const series: echarts.SeriesOption[] = legend.map((item, index) => {
    return {
      name: item.label,
      type: 'bar',
      stack: 'total',
      data: normalizedData.map(group => group[index] ?? 0),
      itemStyle: {
        color: colors[index]
      },
      barWidth: '60%',
      label: {
        show: true,
        formatter: (params: any) => {
          const original = dataGroups[params.dataIndex]?.[index] ?? 0
          return original > 0 ? original.toFixed(1) : ''
        },
        fontSize: 11,
        color: '#333',
        fontWeight: 'bold'
      },
      labelLayout: (params: any) => {
        const { rect } = params
        const segmentTop = rect.y
        return {
          x: rect.x + rect.width + 5,
          y: segmentTop,
          align: 'left',
          verticalAlign: 'bottom'
        }
      }
    }
  })

  // 用scatter单独回执logo，并通过symbolOffset控制与柱顶的像素间隙
  const logoSize = 24 // logo 宽高（像素）
  const logoOffsetY = -25 // logo 向上偏移多少像素（负数向上），增大绝对值增大空隙
  const logoScatter: echarts.SeriesOption = {
    type: 'scatter',
    data: seriesData.map((item, index) => {
      return {
        name: item.method,
        value: [item.method, maxValues[index]],
        symbol: `image://${item.src}`,
        symbolSize: [logoSize, logoSize],
      }
    }),
    symbolOffset: [0, logoOffsetY],
    silent: true,
    tooltip: { show: false },
    z: 120
  }

  series.push(logoScatter)

  const option: echarts.EChartsOption = {
    backgroundColor: '#fff',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        if (!params || params.length === 0) return ''

        const index = params[0].dataIndex
        let text = `${categoryData[index]}<br/>`

        params.forEach((param: any) => {
          const segIndex = legend.findIndex(item => item.label === param.seriesName)
          if (segIndex >= 0) {
            const orig = dataGroups[index]?.[segIndex] ?? 0
            if (orig) {
              text += `${param.marker} ${param.seriesName}: ${orig.toFixed(1)}<br/>`;
            }
          }
        })

        return text
      }
    },
    legend: {
      top: '5%',
      textStyle: {
        color: '#333',
        fontSize: 12,
      },
      data: legend.map(item => item.label),
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      top: '20%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: categoryData,
      axisLabel: { rotate: 25, color: '#666', fontSize: 12 },
      axisLine: { lineStyle: { color: '#ccc' } },
    },
    yAxis: {
      type: 'value',
      name: 'Score',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: { color: '#888', fontSize: 12 },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } },
    },
    series
  }

  chart.setOption(option)
}

defineExpose({ renderChart })
</script>

<style lang="scss" scoped>
.chart {
  width: 100%;
  height: 400px;
}
</style>