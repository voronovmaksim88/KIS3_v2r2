// src/components/TheOrders.vue
<script setup lang="ts">
import {onMounted} from 'vue';
import {storeToRefs} from 'pinia';
import {useOrdersStore} from '../stores/storeOrders';
import BaseButton from "@/components/Buttons/BaseButton.vue"; // Убедитесь, что путь к стору правильный

// 1. Получаем экземпляр стора
const ordersStore = useOrdersStore();

// 2. Извлекаем реактивные переменные и действия из стора.
// Используем storeToRefs для сохранения реактивности состояния и вычисляемых свойств
const {
  orders,      // Список заказов для текущей страницы
  isLoading,   // Состояние загрузки (уже используется в шаблоне)
  error,       // Состояние ошибки (уже используется в шаблоне)
  totalOrders, // Общее количество заказов
  currentPage, // Текущая страница (вычисляемое)
  totalPages,  // Всего страниц (вычисляемое)
  currentLimit,// Текущий лимит на странице
  currentSkip // Текущий пропуск записей
} = storeToRefs(ordersStore);

// Действия можно извлекать напрямую
const {fetchOrders, clearError} = ordersStore;

// 3. Вызываем действие fetchOrders при монтировании компонента
onMounted(() => {
  // Загружаем первую страницу с параметрами по умолчанию (или задаем свои)
  // Например, fetchOrders({skip: 0, limit: 10});
  fetchOrders({skip: 0, limit: 20});
});

// 4. Функции для пагинации (вызывают fetchOrders с новыми параметрами)
const goToPreviousPage = () => {
  if (currentPage.value > 0) {
    const newSkip = currentSkip.value - currentLimit.value;
    fetchOrders({skip: newSkip, limit: currentLimit.value});
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    const newSkip = currentSkip.value + currentLimit.value;
    fetchOrders({skip: newSkip, limit: currentLimit.value});
  }
};

function addNewOrder() {

}

function findOrders() {

}

</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4 text-white">

    <div v-if="isLoading" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-if="!isLoading && error"
         class="w-full bg-red-500 text-white p-4 rounded mb-4 flex justify-between items-center">
      <span>Ошибка: {{ error }}</span>
      <div>
        <button @click="fetchOrders({ skip: currentSkip, limit: currentLimit })"
                class="ml-4 p-1 px-2 bg-red-700 rounded hover:bg-red-600 text-xs">
          Повторить
        </button>
        <button @click="clearError" class="ml-2 p-1 px-2 bg-gray-600 rounded hover:bg-gray-500 text-xs">
          Скрыть
        </button>
      </div>
    </div>

    <div v-if="!isLoading && !error" class="w-full">
      <table class="min-w-full bg-gray-700 rounded-lg mb-4 table-fixed">
        <colgroup>
          <col style="width: 8%"> <!-- номер заказа -->
          <col style="width: 22%"> <!-- Заказчик -->
          <col style="width: 10%"> <!-- Приоритет -->
          <col style="width: 25%"> <!-- Название -->
          <col style="width: 15%"> <!-- Виды работ -->
          <col style="width: 20%"> <!-- Статус -->
        </colgroup>
        <thead>
        <tr>
          <th colspan="7" class="px-2 py-2 text-center bg-gray-600 ">
            <div class="px-1 py-1 bg-gray-600 flex justify-end items-center">
              <BaseButton
                  :action="addNewOrder"
                  :text="'Поиск'"
                  :style="'Primary'"
                  class="px-1"
              />

              <BaseButton
                  :action="findOrders"
                  :text="'Добавить'"
                  :style="'Success'"
                  class="px-1"
              />
            </div>
          </th>
        </tr>
        <tr>
          <th class="px-4 py-2 text-left">Номер</th>
          <th class="px-4 py-2 text-left">Заказчик</th>
          <th class="px-4 py-2 text-left">Приоритет</th>
          <th class="px-4 py-2 text-left">Название</th>
          <th class="px-4 py-2 text-left">Виды работ</th>
          <th class="px-4 py-2 text-left">Статус</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="order in orders" :key="order.serial" class="border-t border-gray-600">
          <td class="px-4 py-2"
              :class="{
              'font-bold': [1, 2, 3, 4, 8].includes(order.status_id),
              'text-yellow-400': order.status_id === 1,
              'text-blue-400': order.status_id === 2,
              'text-green-400': order.status_id === 3,
              'text-red-400': order.status_id === 4
              }"
          >
            {{ order.serial }}
          </td>
          <td class="px-4 py-2">{{ order.customer }}</td>
          <td class="px-4 py-2">{{ order.priority ?? '-' }}</td>
          <td class="px-4 py-2">{{ order.name }}</td>
          <td class="px-4 py-2">
            <p v-for="work in order.works" :key="work.id">
              {{ work.name }}
            </p>
          </td>
          <td
              class="px-4 py-2"
              :class="{
              'font-bold': [1, 2, 3, 4, 8].includes(order.status_id),
              'text-yellow-400': order.status_id === 1,
              'text-blue-400': order.status_id === 2,
              'text-green-400': order.status_id === 3,
              'text-red-400': order.status_id === 4
              }"
          >
            {{ ordersStore.getStatusText(order.status_id) }}
          </td>
        </tr>
        </tbody>
      </table>

      <div v-if="totalPages > 1" class="mt-6 flex justify-center items-center space-x-3">
        <button
            @click="goToPreviousPage"
            :disabled="currentPage === 0"
            class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Назад
        </button>
        <span class="text-lg">
          Страница {{ currentPage + 1 }} из {{ totalPages }}
        </span>
        <button
            @click="goToNextPage"
            :disabled="currentPage >= totalPages - 1"
            class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Вперед
        </button>
      </div>
      <div v-if="!isLoading && orders.length > 0" class="text-center text-gray-400 mt-2 text-sm">
        Показано {{ orders.length }} из {{ totalOrders }} заказов.
      </div>

    </div>

  </div>
</template>

<style scoped>
/* Можно добавить специфичные стили, если нужно */
</style>