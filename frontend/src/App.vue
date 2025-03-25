<!--App.vue-->
<script setup lang="ts">
import { ref } from 'vue'

import TheMain from "./components/TheMain.vue";
import BoxSerialNum from "./components/BoxSerialNum.vue";
import CommercialOffer from "./components/CommercialOffer.vue";
import BD_FastAPI_PostGreSQL from "./components/Test_FastAPI/The_Test_FastAPI.vue";
import The_Test_Data_Base from "./components/TestDataBase/The_Test_Data_Base.vue";
import TheHeader from "@/components/TheHeader.vue";
import {usePagesStore} from "./stores/storePages.ts";

const pageStore = usePagesStore()

const show_KIS = ref(false)
const show_Box_SerialNum = ref(false)
const show_Test_Fast = ref(false)
const show_Commercial_Offer =  ref(false)
const show_Test_Date_Base = ref(false)

function hideAllApp(){
  show_KIS.value = false
  show_Box_SerialNum.value = false
  show_Test_Fast.value = false
  show_Commercial_Offer.value = false
  show_Test_Date_Base.value = false
}

function ButtonShowYchetSnSkafovClicked() {
  hideAllApp()
  show_Box_SerialNum.value = true
}

function ButtonTestFastAPIClicked() {
  hideAllApp()
  show_Test_Fast.value = true
}

function Button_Commercial_Offer_Clicked() {
  hideAllApp()
  show_Commercial_Offer.value = true
}

function ButtonShowTestDataBaseClicked() {
  hideAllApp()
  show_Test_Date_Base.value = true
}
</script>

<template>
  <TheHeader/>

  <TheMain
      v-if="pageStore.selectedPage == 'main'"
      @btnYchetSnSkafov="ButtonShowYchetSnSkafovClicked"
      @btnTestFastAPI="ButtonTestFastAPIClicked"
      @btnCommercialOffer="Button_Commercial_Offer_Clicked"
      @btnTestDataBase="ButtonShowTestDataBaseClicked"
      api-url="http://localhost:8000/api"
  />
  <BoxSerialNum v-if="show_Box_SerialNum"/>
  <BD_FastAPI_PostGreSQL v-if="show_Test_Fast"/>
  <CommercialOffer  v-if="show_Commercial_Offer" />
  <The_Test_Data_Base v-if="show_Test_Date_Base"/>

</template>

<style></style>
