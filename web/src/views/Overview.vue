<template lang="pug">
  Introduction
    .desc.m-top-20 These challenges include:
    ul.p-left-40
      li.desc
        span.bold FinDocResearch
        span : Evaluating the ability to comprehensively analyze 
        span.bold multiple financial documents 
        span (i.e., annual reports) of listed companies across 
        span.bold 8 financial markets
        span .
      li.desc
        span.bold FinDeepResearch
        span : Assessing the capability for conducting rigorous 
        span.bold corporate financial analysis 
        span for 
        span.bold listed companies across 8 financial markets 
        span by retrieving and analyzing their associated heterogeneous financial data, such as 
        span.underline company disclosures, financial news, historical stock prices, market indexes
        span , etc.
      li.desc
        span.bold FinDeepForecast
        span : Verifying the accuracy of 
        span.bold financial forecasts for financial metrics and ratios 
        span of listed companies from 
        span.bold 9 stock exchanges 
        span and broader 
        span.bold macroeconomic indicators 
        span across 
        span.bold 8 countries/regions
        span .
      li ...
  .section
    .title Organizers
    .list
      .list-item(:style="{padding: '0'}" @click="navigateTo('https://www.nus.edu.sg/')")
        img(src="/images/organizer/nus.jpg")
      .list-item(@click="navigateTo('https://www.nextcenter.org/')")
        img(src="/images/organizer/next.png")
      .list-item(:style="{padding: '0'}" @click="navigateTo('https://www.aidf.nus.edu.sg/')")
        img(src="/images/organizer/aidf.jpg")
      .list-item(:style="{padding: '0 10px'}" @click="navigateTo('https://www.6estates.com/')")
        img(src="/images/organizer/6Estates.jpg")
      .list-item(@click="navigateTo('https://www.bloomberg.com/')")
        img(src="/images/organizer/bloomberg.jpg")
      .list-item(:style="{padding: '0'}" @click="navigateTo('https://www.hfut.edu.cn/')")
        img(src="/images/organizer/hfut.jpeg" :style="{width: '120px', height: '120px'}")
      .list-item(:style="{padding: '0'}" @click="navigateTo('https://ustc.edu.cn/')")
        img(src="/images/organizer/ustc.jpg" :style="{width: '120px', height: '120px'}")
  .section
    .title Sponsors
    .list
      .list-item(:style="{padding: '0 10px'}" @click="navigateTo('https://www.6estates.com/')")
        img(src="/images/organizer/6Estates.jpg")
  .section
    .title Contact
    .desc
      span The OpenFinArena team is open to collaboration across development, application, and partnership. Whether you have inquiries, technical questions, or are interested in contributing to the evolution of this platform, please join the 
      a.link.link-green(href="https://groups.google.com/g/openfinarena" target="_blank") OpenFinArena Google Group 
      span or drop us an email at 
      span.email OpenFinArena@gmail.com
      span .
</template>

<script setup lang="ts">
const navigateTo = (url: string) => {
  window.open(url, '_blank')
}
</script>

<style lang="scss" scoped>
.subtitle {
  color: #e8a107;
}

.leader-name {
  color: #666;
  font-weight: 700;
}

.leader-role {
  color: #666;
  font-weight: 300;
}

.list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;

  &-item {
    padding: 0 20px;
    display: flex;
    display: -webkit-flex;
    align-items: center;
    justify-content: center;
    height: 160px;
    width: 200px;
    background: #fff;
    border-radius: 24px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    cursor: pointer;

    &:hover {
      transform: scale(1.05);
      filter: brightness(1.1);
    }
  }

  img {
    width: 100%;
  }
}
</style>
