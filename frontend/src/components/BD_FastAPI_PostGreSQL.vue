<script setup>
import {ref} from 'vue'
import The_Test_FastAPI_hello_world from "@/components/The_Test_FastAPI_hello_world.vue";
import The_Test_FastAPI_hello_name from "@/components/The_Test_FastAPI_hello_name.vue";
import The_Test_FastAPI_fetch_fake_user from "@/components/The_Test_FastAPI_fetch_fake_user.vue";
import The_Test_FastAPI_get_html_page from "@/components/The_Test_FastAPI_get_html_page.vue";


const error_TestLoadFile = ref(null)

// const backend_url = "https://sibplc-kis3.ru/api/"
const backend_url = "http://localhost:8000/api/"
const mul1 = ref(0) //  множитель 1
const mul2 = ref(0) //  множитель 2
const composition = ref(0) // произведение





const fetchTestFile = async () => {
  error_TestLoadFile.value = null;
  try {
    const response = await fetch(`${backend_url}test/load_test_file`);

    if (!response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('test_file not found!!!');
    }

    // Здесь нужно добавить обработку успешного ответа
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = 'test_file.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);

  } catch (err) {
    error_TestLoadFile.value = err.message;
  }
};


const a = ref(0)
const b = ref(0)
const c = ref(0)

async function fetchSumma() {
  // отправляем запрос
  const response = await fetch(`${backend_url}test/summa`, {
    method: "POST",
    headers: {"Accept": "application/json", "Content-Type": "application/json"},
    body: JSON.stringify({
      a: a.value,
      b: b.value
    })
  });
  if (response.ok) {
    const data = await response.json();
    c.value = data.message;
  } else
    console.log(response);
}


async function fetchMultiplication() {
  // отправляем запрос
  const response = await fetch(`${backend_url}test/mult`, {
    method: "POST",
    headers: {"Accept": "application/json", "Content-Type": "application/json"},
    body: JSON.stringify({
      m1: mul1.value,
      m2: mul2.value
    })
  });
  if (response.ok) {
    const data = await response.json();
    composition.value = data.message;
  } else
    console.log(response);
}

// функция получает список всех стран из БД PostgreSQL
const all_countries = ref("") // список всех стран
const all_countries_error = ref("") // список всех стран
async function fetchCountry() {
  all_countries.value = ""; // изначально обнуляем список стран
  const timeout = 3000; // 3 секунды
  const fetchPromise = fetch(`${backend_url}all_countries`);
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
      all_countries_error.value = ""; // если получен ответ скидываем ошибку
    } else {
      console.log('Response not OK:', response);
    }
  } catch (error) {
    if (error.message === 'Request timed out') {
      console.error('Request timed out after', timeout, 'ms');
    } else {
      console.error('Error fetching countries:', error);
    }
    all_countries_error.value = error;
    all_countries.value = "";
  }
}

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

      <The_Test_FastAPI_hello_world :url="backend_url"/>
      <The_Test_FastAPI_hello_name :url="backend_url"/>
      <The_Test_FastAPI_fetch_fake_user :url="backend_url"/>
      <The_Test_FastAPI_get_html_page :url="backend_url"/>




      <div class="grid grid-cols-3 gap-2">
        <button class="btn btn-p" @click="fetchTestFile">Load test file</button>
        <div v-if="error_TestLoadFile">
          <p style="color: red;">{{ error_TestLoadFile }}</p>
        </div>
      </div>
      <hr class="mb-5">

      <div class="grid grid-cols-3 gap-2">
        <button class="btn btn-p" @click="fetchSumma">Get sum</button>
        <div class="flex flex-row gap-2">
          <input
              class="w-1/2 rounded-md"
              type="number"
              v-model="a"
              title="Введите первое слагаемое"
          />
          <input
              class="w-1/2 rounded-md"
              type="number"
              v-model="b"
              title="Введите второе слагаемое"
          />
        </div>
        <p class="text-white">{{ c }}</p>
      </div>
      <hr class="mb-5">

      <div class="grid grid-cols-3 gap-2">
        <button class="btn btn-p" @click="fetchMultiplication">Get multiplication</button>
        <div class="flex flex-row gap-2">
          <input
              class="w-1/2 rounded-md"
              type="number"
              v-model="mul1"
              title="Введите первый множитель"
          />
          <input
              class="w-1/2 rounded-md"
              type="number"
              v-model="mul2"
              title="Введите второй множитель"
          />
        </div>
        <p class="text-white">{{ composition }}</p>
      </div>
      <hr class="mb-5">

      <div class="grid grid-cols-3 gap-2">
        <button class="btn btn-p" @click="fetchCountry">Get country from DB</button>
        <div v-if="all_countries && all_countries.length > 0">
          <table class="text-white">
            <thead>
            <tr>
              <th>id</th>
              <th>name</th>
            </tr>
            </thead>
            <tr v-for="country in all_countries" :key="country.id">
              <td>{{ country.id }}</td>
              <td>{{ country.name }}</td>
            </tr>
          </table>
        </div>
        <p class="text-red-400" v-if="all_countries_error">{{ all_countries_error }}</p>
      </div>
      <hr class="mb-5">

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