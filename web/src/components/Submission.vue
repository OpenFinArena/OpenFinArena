<template lang="pug">
  .section
    .title Submission
    .desc
      span To submit the predictions of your method, please send your results in 
      span.subtitle Markdown 
      span format to 
      span.email OpenFinArena@gmail.com
      span(v-if="showMethodType") . The name of the predicted report should follow the pattern in the samples. For example, if the Case ID is
      span(v-else) . The predicted report should use the Case ID as the file name like the sample reports. For example, if the Case ID is 
      span.underline "test001"
      span , the file name should be 
      span.underline(v-if="showMethodType") "test001-report.md"
      span.underline(v-else) "test001.md"
      span .
    .desc.m-top-20
      span Please use the following subject in your email: 
      span.bold {{emailTitle}}
      span .
    .desc.m-top-20
      span The 
      span.bold Method Name 
      span should be a unique name for your system/method, not just the name of the base model used (e.g., "MyAwesomeMethod", "FinAgent-v2", not "GPT-4").
    .desc.m-top-20(v-if="showMethodType")
      span The 
      span.bold Method Type 
      span might be "Thinking", "Thinking + Search", "Deep Research" or other types that can best explain the type of your method. If the method type cannot be confirmed or you choose not to disclose it, please indicate "Other". 
    .desc.m-top-20
      span If you have a dedicated logo for your Organization, please attach the logo in the size of 100x100, such as 
      img(src="/images/logo/openai.svg" style="width:25px; height:25px; margin-left:5px; margin-right:5px")
      span for OpenAI, which will be presented in the leaderboard.
</template>

<script setup lang="ts">
const props = defineProps<{
  emailTitle: string
  showMethodType: boolean
}>()
</script>
