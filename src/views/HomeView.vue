<template lang="pug">
  Header
  .container
    router-view
</template>

<script setup lang="ts">
import Header from '@/components/Header.vue'
</script>

<style lang="scss" scoped>
.container {
  padding: 2% 4%;
}
</style>
