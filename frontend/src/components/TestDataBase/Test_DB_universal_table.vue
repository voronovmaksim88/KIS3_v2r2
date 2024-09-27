<script setup>
import { ref } from 'vue'

const props = defineProps({
  url: {
    type: String,
    required: true
  },
  endpoint: {
    type: String,
    required: true
  },
  buttonText: {
    type: String,
    default: 'Получить данные'
  },
  maxHeight: {
    type: String,
    default: '400px'
  }
});

const tableData = ref([])
const tableHeaders = ref([])
const connectionError = ref('')

async function fetchData() {
  connectionError.value = '';
  tableData.value = [];
  tableHeaders.value = [];

  const timeout = 3000;
  const fetchPromise = fetch(`${props.url}${props.endpoint}`);
  const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Превышено время ожидания запроса')), timeout)
  );

  try {
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    console.log('Статус ответа:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Полученные данные:', data);

      const arrayKey = Object.keys(data).find(key => Array.isArray(data[key]));

      if (arrayKey && data[arrayKey].length > 0) {
        tableData.value = data[arrayKey];
        tableHeaders.value = Object.keys(data[arrayKey][0]);
      } else {
        // noinspection ExceptionCaughtLocallyJS
        throw new Error('Некорректный формат данных');
      }
    } else {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('Ошибка при получении данных');
    }
  } catch (error) {
    console.error('Ошибка при получении данных:', error);
    connectionError.value = error.message;
  }
}

function clearData() {
  tableData.value = []
  tableHeaders.value = []
  connectionError.value = ""
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <div class="col-span-1">
      <button class="btn btn-p w-full" @click="fetchData">{{ buttonText }}</button>
    </div>

    <div>
      <button class="btn btn-s" @click="clearData">Свернуть</button>
    </div>

    <div class="col-span-4" v-if="tableData.length > 0">
      <div class="overflow-x-auto">
        <div :style="{ maxHeight: props.maxHeight, overflowY: 'auto' }">
          <table class="w-full bg-gray-700">
            <thead>
            <tr>
              <th v-for="header in tableHeaders" :key="header" class="sticky bg-gray-600 top-0 z-10">{{ header }}</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(row, index) in tableData" :key="index">
              <td v-for="header in tableHeaders" :key="header">
                {{ row[header] }}
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <p class="text-red-400 col-span-4" v-if="connectionError">{{ connectionError }}</p>

  </div>
</template>

<style scoped>
th {
  position: sticky;
  top: 0;
  z-index: 10;
}
</style>