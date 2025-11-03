<template lang="pug">
  .header
    .caption
      .caption-title OpenFinArena
      .caption-subtitle.m-top-10 Evaluating LLMs and Agents in Rigorous Financial Analysis and Forecasting
    .navs
      .nav-item(
        v-for="item in navs"
        :key="item.path"
        :class="{'active': item.path === currentPath}"
        @click="$router.push(item.path)"
      ) {{ item.title }}
      el-popover(popper-class="for-more" :width="265")
        .for-more-content
          img(src="/images/coming-soon.svg")
          span Stay tuned for more challenges...
        template(#reference)
          .nav-item.more ...
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const navs = [
  {
    title: 'Overview',
    path: '/'
  },
  {
    title: 'FinDocResearch',
    path: '/fin-doc-research'
  },
  {
    title: 'FinDeepResearch',
    path: '/fin-deep-research'
  },
  {
    title: 'FinDeepForecast',
    path: '/fin-deep-forecast'
  }
]

const currentPath = computed<string>(() => {
  return route.path
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  display: -webkit-flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7% 2%;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1);
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 1000;

  .caption {
    line-height: 32px;

    &-title {
      color: #e8a107;
      font-size: 36px;
      font-weight: 900;
    }

    &-subtitle {
      font-size: 20px;
      color: #666;
    }
  }

  .navs {
    display: flex;
    display: -webkit-flex;
    flex-wrap: wrap;
    column-gap: 40px;
    row-gap: 5px;
    padding-left: 10px;

    .nav-item {
      font-size: 16px;
      color: #000;

      &.active {
        color: #e8a107;
        font-weight: bold;
      }

      &:hover {
        cursor: pointer;
      }
    }
    .more:hover {
      color: #e8a107;
    }
  }
}
</style>
