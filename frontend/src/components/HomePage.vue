<script setup>
const emit = defineEmits([
  'btnKis',
  'btnYchetSnSkafov',
  'btnTestFastAPI',
  'btnCommercialOffer',
  'btnTestDataBase'])

function fnBtnKis() {
  emit('btnKis')
}

function fnBtnYchetSnSkafov() {
  emit('btnYchetSnSkafov')
}

function fnBtnTestFastAPI() {
  emit('btnTestFastAPI')
}

function fnBtnCommercialOffer() {
  emit('btnCommercialOffer')
}

function fnBtnTestDataBase() {
  emit('btnTestDataBase')
}

</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4">
    <h1 class="text-green-400 text-3xl mb-5 text-center">SibPLC-web</h1>
    <div class="flex flex-col w-full sm:w-1/2 md:w-1/3 lg:w-1/4 xl:w-1/6 space-y-4">
      <button class="btn btn-p" @click="fnBtnTestFastAPI">Тест FastAPI</button>
      <button class="btn btn-p" @click="fnBtnTestDataBase">Тест DataBase</button>
      <button class="btn btn-p" @click="fnBtnKis">КИС</button>
      <button class="btn btn-p" @click="fnBtnYchetSnSkafov">Учёт с/н шкафов</button>

      <button class="btn btn-s" @click="fnBtnCommercialOffer">Составление КП</button>
      <button class="btn btn-s" >Бланк ТЗ для ШАОВ</button>
      <button class="btn btn-s" >Расчёт стоимости ША</button>
      <button class="btn btn-s" >Подбор ПЛК</button>
    </div>
  </div>
</template>

<style scoped></style>
