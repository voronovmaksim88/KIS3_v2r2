<script setup>

import The_Test_DB_countries from "./The_Test_DB_countries.vue";
import The_Test_DB_manufacturers from "./The_Test_DB_manufacturers.vue";
import The_Test_DB_equipment_types from "./The_Test_DB_equipment_types.vue";

// const backend_url = "https://sibplc-kis3.ru/api/"
// const backend_url = "http://localhost:8000/api/"
const backend_url = import.meta.env.VITE_API_URL; // Если используете Vite


</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800" id="BD_FastAPI_PostGreSQL">
    <div class="flex flex-col w-full sm:w-1/2 md:w-2/3 lg:w-2/3 xl:w-5/12 space-y-4">
      <h1 class="text-green-400 text-3xl mb-5">Test FastApi</h1>

      <The_Test_DB_countries :url="backend_url"/>
      <The_Test_DB_manufacturers :url="backend_url"/>
      <The_Test_DB_equipment_types :url="backend_url"/>

    </div>
  </div>
</template>

<style scoped>

</style>