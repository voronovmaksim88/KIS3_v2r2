<script setup>
import {ref} from 'vue'
import The_Test_DB_countries from "./The_Test_DB_countries.vue";

// const backend_url = "https://sibplc-kis3.ru/api/"
// const backend_url = "http://localhost:8000/api/"
const backend_url = import.meta.env.VITE_API_URL; // Если используете Vite


// функция получает список всех производителей из БД PostgreSQL
const all_manufacturers = ref("") // список всех стран
const all_manufacturers_error = ref("") // список всех стран
async function fetchManufacturers() {
  all_manufacturers.value = ""; // изначально обнуляем список стран
  const timeout = 3000; // 3 секунды
  const fetchPromise = fetch(`${backend_url}all_manufacturers`);
  const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timed out')), timeout)
  );

  /**
   * @typedef {Object} ServerResponse
   * @property {string[]} manufacturers
   */

  /**
   * @param {ServerResponse} data
   */
  try {
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    console.log('Response status:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Received data:', data);
      all_manufacturers.value = data.manufacturers;
      all_manufacturers_error.value = ""; // если получен ответ скидываем ошибку
    } else {
      console.log('Response not OK:', response);
    }
  } catch (error) {
    if (error.message === 'Request timed out') {
      console.error('Request timed out after', timeout, 'ms');
    } else {
      console.error('Error fetching countries:', error);
    }
    all_manufacturers_error.value = error;
    all_manufacturers.value = "";
  }
}
</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800" id="BD_FastAPI_PostGreSQL">
    <div class="flex flex-col w-full sm:w-1/2 md:w-2/3 lg:w-2/3 xl:w-5/12 space-y-4">
      <h1 class="text-green-400 text-3xl mb-5">Test FastApi</h1>

      <The_Test_DB_countries :url="backend_url"/>

      <div class="grid grid-cols-3 gap-2">
        <button class="btn btn-p" @click="fetchManufacturers">Get Manufacturers from DB</button>
        <div v-if="all_manufacturers && all_manufacturers.length > 0">
          <table>
            <thead>
            <tr>
              <th>id</th>
              <th>name</th>
              <th>country_id</th>
            </tr>
            </thead>
            <tr v-for="manufacturer in all_manufacturers" :key="manufacturer.id">
              <td>{{ manufacturer.id }}</td>
              <td>{{ manufacturer.name }}</td>
              <td v-if="'country_id' in manufacturer">{{ manufacturer.country_id }}</td>
              <td v-else>N/A</td>
            </tr>
          </table>
        </div>
        <p class="text-red-400" v-if="all_manufacturers_error">{{ all_manufacturers_error }}</p>
      </div>
      <hr class="mb-5">

    </div>
  </div>
</template>

<style scoped>

</style>