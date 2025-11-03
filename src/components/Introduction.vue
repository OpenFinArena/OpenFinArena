<template lang="pug">
  .section
    .title {{intros[currentPath].title}}
    .desc(v-html="intros[currentPath].desc")
    slot
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()

const intros = {
  '/': {
    title: 'Overview',
    desc: `The <span class="bold">OpenFinArena</span> platform aims to gauge the proficiency of advanced Language Models (LLMs) and  Agents in executing rigorous financial analysis and forecasting, establishing a robust standard for their development as <span class="bold">professional financial analysts and economists</span>. OpenFinArena offers a comprehensive suite of challenges, spanning financial document analysis, corporate financial analysis, financial nowcasting, and future forecasting.`
  },
  '/fin-doc-research': {
    title: 'Financial Document Research (FinDocResearch)',
    desc: `The accurate and timely interpretation of corporate financial disclosures, such as financial statements, is critical for informed decision-making (e.g., investment) in finance. However, the complexity and knowledge-intensive nature of these documents often render their analysis a time-consuming and laborious process. The application of Artificial Intelligence (AI) techniques presents a transformative opportunity to automate this process to provide actionable intelligence from these documents. <span class="bold">Financial Document Research (FinDocResearch)</span> is therefore designed to evaluate the capabilities of advanced AI techniques, such as LLMs and Agents, in <span class="bold">comprehensively analyzing a listed company's multi-year annual reports and producing a rigorous, structured research report</span>. FinDocResearch features <span class="bold">80 listed companies</span> from <span class="bold">8 financial markets</span>, including United States (US), United Kingdom (UK), China(CN), Hong Kong (HK), Australia (AU), Singapore (SG), Malaysia (MY) and Indonesia (ID). By simulating the workflows of professional research analysts, FinDocResearch establishes a novel benchmark for assessing cross-document research methodologies in financial AI.`
  },
  '/fin-deep-research': {
    title: 'Financial Deep Research (FinDeepResearch)',
    desc: `<span class="bold">Corporate financial analysis</span> 
          is a critical process for understanding a listed company's business health, financial performance, and stock valuation, ultimately guiding investment decisions.  Professional analysts typically execute a comprehensive and rigorous workflow, beginning with the retrieval and recognition of relevant data from diverse sources, such as corporate disclosures, financial news, historical stock prices, and market indexes. The data is then used for metric calculation, followed by strategic summarization and interpretation, aggregating in the generation of a research report to inform decision-making. 
          <span class="bold">FinDeepResearch</span> 
          is specifically designed to emulate this professional pipeline to 
          <span class="bold">conduct corporate financial analysis following an expert-designed analytical structure to generate a rigorous, structured report</span>. Comprising 
          <span class="bold">64 listed companies from 8 financial markets</span> and a total of <span class="bold">15,808 grading items</span>, FinDeepResearch provides a robust framework for evaluating the ability of advanced AI techniques (e.g., deep research agents) to generate corporate financial analysis reports that simultaneously adhere to a 
          <span class="bold">systematic analytical structure (rigor)</span> and produce <span class="bold">specific, accurate claims (precision)</span>.`
  },
  '/fin-deep-forecast': {
    title: 'Financial Deep Forecasting (FinDeepForecast)',
    desc: `The current paradigm for evaluating Large Language Models (LLMs) and AI Agents in financial analysis is constrained by its reliance on 
    <span class="bold">static, historical datasets</span>. This approach primarily assesses a model's capacity to interpret past events rather than forecast future outcomes. This methodological misalignment with real-world practice fails to simulate the 
    <span class="bold">dynamic, looking-forward</span> environments that analysts and economists face. To address this critical gap, we introduce <span class="bold">FinDeepForecast</span>, a live benchmark for evaluating the 
    <span class="bold">genuine financial forecasting capabilities</span> of LLMs and AI agents. It challenges models to make time-sensitive predictions on the future 
    <span class="bold">financial metrics and ratios of listed companies from 9 global stock exchanges</span>, as well as 
    <span class="bold">broader macroeconomic indicators across 8 countries/regions</span>. Crucially, the accuracy of these forecasts can only be verified by future outcomes, providing a dynamic and realistic assessment of model performance.`
  }
}

const currentPath = computed<string>(() => {
  return route.path
})
</script>
