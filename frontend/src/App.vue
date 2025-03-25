<!--App.vue-->
<script setup lang="ts">

import TheMain from "./components/TheMain.vue";
import BoxSerialNum from "./components/BoxSerialNum.vue";
//import CommercialOffer from "./components/CommercialOffer.vue";
import TheTestFastAPI from "./components/Test_FastAPI/The_Test_FastAPI.vue";
import TheTestDataBase from "./components/TestDataBase/TheTestDataBase.vue";
import TheHeader from "@/components/TheHeader.vue";
import {usePagesStore} from "./stores/storePages.ts";

const pageStore = usePagesStore()


</script>

<template>
  <TheHeader/>

  <TheMain
      v-if="pageStore.selectedPage == 'main'"
      api-url="http://localhost:8000/api"
  />
  <BoxSerialNum v-if="pageStore.selectedPage == 'box-serial-num'"/>
  <TheTestFastAPI v-if="pageStore.selectedPage == 'test-fastapi'"/>
  <TheTestDataBase v-if="pageStore.selectedPage == 'test-db'"/>
  <!--  <CommercialOffer  v-if="" />-->


</template>

<style></style>
