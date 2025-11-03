<template lang="pug">
  .links.m-top-20
    .link-item(
      v-for="(link, index) in getLink()"
      :key="link.name"
      :class="{'active': index === 0}"
      @click="openLink(link.href)"
    )
      img(:src="`/images/link/${link.icon}.svg`" :style="{width: link.width || '22px'}")
      span {{link.name}}
      .sub-name(v-if="link.subName") {{link.subName}}
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentPath = computed<string>(() => route.path)

const docResearch = [
  {
    name: 'Grand Challenge @ ICAIF 25',
    href: 'https://finddr2025.github.io/',
    icon: 'web'
  },
  {
    name: 'Technical Report',
    subName: '(Coming soon)',
    href: '',
    icon: 'report'
  },
  {
    name: 'Hugging Face',
    href: 'https://huggingface.co/datasets/OpenFinArena/FinDocResearch',
    icon: 'huggingface'
  },
  {
    name: 'Github',
    href: 'https://github.com/OpenFinArena/OpenFinArena',
    icon: 'github'
  }
]

const deepResearch = [
  {
    name: 'Paper',
    href: 'https://www.arxiv.org/abs/2510.13936',
    icon: 'arxiv',
    width: '40px'
  },
  {
    name: 'Hugging Face',
    href: 'https://huggingface.co/datasets/OpenFinArena/FinDeepResearch',
    icon: 'huggingface'
  },
  {
    name: 'Github',
    href: 'https://github.com/OpenFinArena/OpenFinArena',
    icon: 'github'
  }
]

const deepForecast = [
  {
    name: 'Technical Report',
    subName: '(Coming soon)',
    href: '',
    icon: 'report'
  },
  {
    name: 'Ongoing Forecasts',
    href: '#ongoing',
    icon: 'forecast'
  },
  {
    name: 'Completed Forecasts',
    href: '#completed',
    icon: 'forecast'
  },
  {
    name: 'Hugging Face',
    href: 'https://huggingface.co/datasets/OpenFinArena/FinDeepForecast',
    icon: 'huggingface'
  },
  {
    name: 'Github',
    href: 'https://github.com/OpenFinArena/OpenFinArena',
    icon: 'github'
  }
]

const getLink = () => {
  switch (currentPath.value) {
    case '/fin-doc-research':
      return docResearch
    case '/fin-deep-research':
      return deepResearch
    case '/fin-deep-forecast':
      return deepForecast
    default:
      return []
  }
}

const openLink = (href: string) => {
  if (!href) return

  if (href.indexOf('#') !== 0) {
    window.open(href, '_blank')
  } else {
    const header = document.querySelector('.header')
    const headerHeight = header?.clientHeight || 0
    document.documentElement.style.setProperty(
      '--scroll-margin',
      `${headerHeight}px`
    )

    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style lang="scss" scoped>
.links {
  margin-bottom: 50px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
  justify-content: center;
}

.link-item {
  padding: 10px 20px;
  border-radius: 30px;
  background: #ffffff;
  border: 2px solid #e8a107;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  font-size: 18px;
  color: #383838;
  cursor: pointer;

  span {
    font-weight: bold;
  }
}

img {
  margin-right: 7px;
  width: 22px;
}

.active {
  background: #e8a107;

  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);

  span {
    color: #fff;
  }
}

.sub-name {
  margin-left: 5px;
  font-size: 12px;
  color: #808080;
  font-weight: 400;
}
</style>
