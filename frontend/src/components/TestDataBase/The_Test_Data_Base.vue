<script setup>

import Test_DB_universal_table from "./Test_DB_universal_table.vue";

// const backend_url = "https://sibplc-kis3.ru/api/"
// const backend_url = "http://localhost:8000/api/"
const backend_url = import.meta.env.VITE_API_URL; // Если используете Vite


</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800" id="BD_FastAPI_PostGreSQL">
    <div class="flex flex-col w-full sm:w-1/2 md:w-2/3 lg:w-2/3 xl:w-5/12 space-y-4">
      <h1 class="text-green-400 text-3xl mb-5">Test Data Base</h1>

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_countries"
          buttonText="Страны"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_manufacturers"
          buttonText="Производителей"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_equipment_types"
          buttonText="Типы оборудования"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_currencies"
          buttonText="Валюты"
      />

    </div>
  </div>
</template>

<style scoped>

</style>