<script setup>
import { ref } from 'vue'

import HomePage from "@/components/HomePage.vue";
import KIS from "@/components/KIS.vue";
import BoxSerialNum from "@/components/BoxSerialNum.vue";
import CommercialOffer from "@/components/CommercialOffer.vue";
import BD_FastAPI_PostGreSQL from "@/components/BD_FastAPI_PostGreSQL.vue";

const show_Home = ref(true)
const show_KIS = ref(false)
const show_Box_SerialNum = ref(false)
const show_Test_Fast = ref(false)
const show_Commercial_Offer =  ref(false)

function hideAllApp(){
  show_KIS.value = false
  show_Box_SerialNum.value = false
  show_Home.value = false
  show_Test_Fast.value = false
  show_Commercial_Offer.value = false
}

function ButtonShowHomeClicked() {
  hideAllApp()
  show_Home.value = true
}

function ButtonShowKisClicked() {
  hideAllApp()
  show_KIS.value = true
}

function ButtonShowYchetSnSkafovClicked() {
  hideAllApp()
  show_Box_SerialNum.value = true
}

function ButtonShowSaitClicked() {
  window.open('https://www.sibplc.ru', '_blank')
}

function ButtonTestFastAPIClicked() {
  hideAllApp()
  show_Test_Fast.value = true
}

function Button_Commercial_Offer_Clicked() {
  hideAllApp()
  show_Commercial_Offer.value = true
}
</script>

<template>
  <button class="btn btn-p" @click="ButtonShowHomeClicked">Home</button>
  <HomePage
      v-if="show_Home"
      @btnKis="ButtonShowKisClicked"
      @btnYchetSnSkafov="ButtonShowYchetSnSkafovClicked"
      @btnSait="ButtonShowSaitClicked"
      @btnTestFastAPI="ButtonTestFastAPIClicked"
      @btnCommercialOffer="Button_Commercial_Offer_Clicked" />
  <KIS v-if="show_KIS"/>
  <BoxSerialNum v-if="show_Box_SerialNum"/>
  <BD_FastAPI_PostGreSQL v-if="show_Test_Fast"/>
  <CommercialOffer  v-if="show_Commercial_Offer" />
</template>

<style></style>
