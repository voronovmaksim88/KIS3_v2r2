<script setup lang="ts">
import BaseButton from '@/components/Buttons/BaseButton.vue'
import {usePagesStore} from "../stores/storePages.ts";


const props = defineProps({
  PageName: {
    type: String,
    default: "My Header" // Значение по умолчанию
  }
})


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
    <p class="ml-auto text-white text-lg">{{ props.PageName }}</p>
  </div>

</template>

<style scoped>

</style>