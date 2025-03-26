<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useBoxAccountingStore } from '../stores/storeBoxAccounting';
import { storeToRefs } from 'pinia';

const boxAccountingStore = useBoxAccountingStore();
const { boxes, isLoading, error, pagination } = storeToRefs(boxAccountingStore);

// URL вашего API-сервера
const apiUrl = ref(import.meta.env.VITE_API_URL || 'http://localhost:8000');

// Загрузка данных при монтировании компонента
onMounted(async () => {
  await boxAccountingStore.fetchBoxes(apiUrl.value);
  console.log('Boxes loaded:', boxes.value.length);
});
</script>

<template>
  <div class="w-full h-screen flex flex-col items-center bg-gray-800 p-4 text-white">
    <h1 class="text-2xl font-bold mb-4">Box Accounting Dashboard</h1>

    <!-- Показываем индикатор загрузки -->
    <div v-if="isLoading" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <!-- Показываем ошибку, если она есть -->
    <div v-if="error" class="w-full bg-red-500 text-white p-4 rounded mb-4">
      {{ error }}
    </div>

    <!-- Показываем данные -->
    <div v-if="!isLoading && boxes.length > 0" class="w-full">
      <div class="overflow-x-auto">
        <table class="min-w-full bg-gray-700 rounded-lg">
          <thead>
          <tr>
            <th class="px-4 py-2 text-left">Serial #</th>
            <th class="px-4 py-2 text-left">Name</th>
            <th class="px-4 py-2 text-left">Order ID</th>
            <th class="px-4 py-2 text-left">Scheme Developer</th>
            <th class="px-4 py-2 text-left">Assembler</th>
            <th class="px-4 py-2 text-left">Programmer</th>
            <th class="px-4 py-2 text-left">Tester</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="box in boxes" :key="box.serial_num" class="border-t border-gray-600">
            <td class="px-4 py-2">{{ box.serial_num }}</td>
            <td class="px-4 py-2">{{ box.name }}</td>
            <td class="px-4 py-2">{{ box.order_id }}</td>
            <td class="px-4 py-2">{{ box.scheme_developer_id }}</td>
            <td class="px-4 py-2">{{ box.assembler_id }}</td>
            <td class="px-4 py-2">{{ box.programmer_id || 'N/A' }}</td>
            <td class="px-4 py-2">{{ box.tester_id }}</td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Пагинация -->
      <div class="flex justify-between items-center mt-4">
        <span>
          Showing {{ boxes.length }} of {{ pagination.total }} boxes
          (Page {{ pagination.page }} of {{ pagination.pages }})
        </span>
        <div class="flex space-x-2">
          <button
              @click="boxAccountingStore.changePage(apiUrl, pagination.page - 1)"
              :disabled="pagination.page <= 1"
              class="px-4 py-2 bg-blue-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
              @click="boxAccountingStore.changePage(apiUrl, pagination.page + 1)"
              :disabled="pagination.page >= pagination.pages"
              class="px-4 py-2 bg-blue-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Сообщение, если данных нет -->
    <div v-if="!isLoading && boxes.length === 0" class="w-full text-center p-8">
      No boxes found. Please add some boxes to get started.
    </div>
  </div>
</template>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0;
}

th, td {
  border-bottom: 1px solid #4b5563;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: rgba(55, 65, 81, 0.7);
}
</style>