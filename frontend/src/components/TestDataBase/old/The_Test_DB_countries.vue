<script setup>
import {ref} from 'vue'

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

// функция получает список всех стран из БД PostgreSQL
const all_countries = ref("") // список всех стран
const connection_error = ref("") // список всех стран
async function fetchCountry() {
  connection_error.value = '';
  all_countries.value = ""; // изначально обнуляем список стран
  const timeout = 3000; // 3 секунды
  const fetchPromise = fetch(`${props.url}all_countries`);
  const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timed out')), timeout)
  );

  try {
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    console.log('Response status:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Received data:', data);
      all_countries.value = data.countries;
      connection_error.value = ""; // если получен ответ скидываем ошибку
    } else {
      console.log('Response not OK:', response);
    }
  } catch (error) {
    if (error.message === 'Request timed out') {
      console.error('Request timed out after', timeout, 'ms');
    } else {
      console.error('Error fetching countries:', error);
    }
    connection_error.value = error.message ;
    all_countries.value = "";
  }
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <div class="col-span-4">
      <button class="btn btn-p " @click="fetchCountry">Get country from DB</button>
    </div>
    <div class="col-span-4" v-if="all_countries && all_countries.length > 0">
      <table class="text-white w-full">
        <thead>
        <tr>
          <th>id</th>
          <th>name</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="country in all_countries" :key="country.id">
          <td>{{ country.id }}</td>
          <td>{{ country.name }}</td>
        </tr>
        </tbody>
      </table>
    </div>
    <p class="text-red-400 col-span-4" v-if="connection_error">{{ connection_error }}</p>
    <hr class="col-span-4 mb-8">
  </div>
</template>

<style scoped>

</style>