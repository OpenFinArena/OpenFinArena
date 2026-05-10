<template lang="pug">
  el-table.m-top-20(:data="sortedList" border)
    el-table-column(label="Rank" width="70" align="center")
      template(#default="scope")
        .rank
          span.medal.gold(v-if="scope.$index === 0") {{scope.$index + 1 }}
          span.medal.silver(v-else-if="scope.$index === 1") {{scope.$index + 1 }}
          span.medal.copper(v-else-if="scope.$index === 2") {{scope.$index + 1 }}
          span(v-else) {{scope.$index + 1 }}
    el-table-column(prop="method" label="Method Name")
    el-table-column(prop="type" label="Method Type")
    el-table-column(prop="organization" label="Organization")
      template(#default="{row}")
        .org
          img(:src="`/images/logo/${row.model}.svg`")
          span {{ row.organization }}
    el-table-column(prop="score" label="Score")
      template(#default="{row}")
        span.bold(v-if="!isNaN(row.score)") {{ Number(row.score).toFixed(1) }}
        span(v-else) {{ row.score }}
    el-table-column(prop="team" label="Team")
    el-table-column(prop="submittedDate" label="Submitted Date")
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ScoreItem {
  [key: string]: any
}

const props = withDefaults(
  defineProps<{
    scoreList?: ScoreItem[]
  }>(),
  {
    scoreList: () => []
  }
)

const sortedList = computed(() => {
  return props.scoreList?.sort((a, b) => {
    return Number(b.score) - Number(a.score)
  })
})
</script>
