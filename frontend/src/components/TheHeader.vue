<script setup lang="ts">
import BaseButton from '@/components/Buttons/BaseButton.vue'
import {usePagesStore} from "../stores/storePages.ts";

const pageStore = usePagesStore()

function GoHome() {
  pageStore.setPage('main')
}
</script>

<template>
  <div class="flex p-2 bg-gray-700">
    <BaseButton
        :text="'Home'"
        :action="GoHome"
        :style="'Primary'"
    />
  </div>

</template>

<style scoped>

</style>