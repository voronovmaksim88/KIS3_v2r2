<!--src/components/TheMain.vue-->
<script setup lang="ts">
import {usePagesStore} from "../stores/storePages.ts";

const pageStore = usePagesStore()


</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4">
    <h1 class="text-green-400 text-3xl mb-5 text-center">SibPLC-web</h1>

    <div class="flex flex-col w-full sm:w-1/2 md:w-1/3 lg:w-1/4 xl:w-1/6 space-y-4">

      <button class="btn btn-p" @click="pageStore.setPage('box-serial-num')">Учёт с/н шкафов</button>
      <button class="btn btn-s">Заказы</button>
      <button class="btn btn-s">Задачи</button>
      <button class="btn btn-s">Тайминги</button>
      <button class="btn btn-p" @click="pageStore.setPage('test-fastapi')">Тест FastAPI</button>
      <button class="btn btn-p" @click="pageStore.setPage('test-db')">Тест базы данных</button>


      <button class="btn btn-s" @click="">Составление КП</button>
      <button class="btn btn-s">Бланк ТЗ для ШАОВ</button>
      <button class="btn btn-s">Расчёт стоимости ША</button>
      <button class="btn btn-s">Подбор ПЛК</button>
    </div>
  </div>
</template>

<style scoped></style>
