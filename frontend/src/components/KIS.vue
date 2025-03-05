<script setup>
import {ref} from 'vue'

const show_task = ref(false)
const show_orders = ref(false)
</script>


<script>
export default {
  data() {
    return {
      countries: []
    }
  },
  methods: {
    async fetchCountries() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/country_api');
        const data = await response.json();
        if (data && 'Countries' in data) {
          this.countries = data.Countries;
        } else {
          console.error('Свойство Countries не найдено в полученных данных');
          this.countries = [];
        }
        console.log(this.countries);
      } catch (error) {
        console.error('Error fetching countries:', error);
      }
    }
  }
}
</script>

<template>
  <div class="w-full h-screen flex flex-col items-center bg-gray-800 ">
    <div class="flex h-full flex-col w-1/6">
      <h1 class="text-green-400 text-3xl mb-5">SibPLC-KIS</h1>
      <button class="btn btn-p" @click="show_orders = true; show_task = false">Заказы</button>
      <button class="btn btn-p" @click="show_task = true; show_orders = false;">Задачи</button>
      <button class="btn btn-p" @click="fetchCountries()">выполнить запрос</button>

      <p v-if="show_orders" class="text-green-200 text-xl"> тут тестово выведем все заказы </p>
      <p v-if="show_task" class="text-green-100 text-xl"> тут тестово выведем все задачи </p>
      <p v-if="show_task" v-for="country in countries">{{ country.name }}</p>
    </div>
  </div>
</template>

<style scoped>
</style>



