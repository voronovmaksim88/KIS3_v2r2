// src/components/TheOrders.vue
<script setup lang="ts">
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useOrdersStore } from '../stores/storeOrders'; // Убедитесь, что путь к стору правильный

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
const { fetchOrders, clearError } = ordersStore;

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
    fetchOrders({ skip: newSkip, limit: currentLimit.value });
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    const newSkip = currentSkip.value + currentLimit.value;
    fetchOrders({ skip: newSkip, limit: currentLimit.value });
  }
};

</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4 text-white">

    <div v-if="isLoading" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-if="!isLoading && error" class="w-full max-w-4xl bg-red-500 text-white p-4 rounded mb-4 flex justify-between items-center">
      <span>Ошибка: {{ error }}</span>
      <div>
        <button @click="fetchOrders({ skip: currentSkip, limit: currentLimit })" class="ml-4 p-1 px-2 bg-red-700 rounded hover:bg-red-600 text-xs">
          Повторить
        </button>
        <button @click="clearError" class="ml-2 p-1 px-2 bg-gray-600 rounded hover:bg-gray-500 text-xs">
          Скрыть
        </button>
      </div>
    </div>

    <div v-if="!isLoading && !error" class="w-full max-w-4xl">
      <h1 class="text-2xl font-semibold mb-4 text-center">Список заказов</h1>

      <div v-if="orders.length > 0" class="space-y-3">
        <div v-for="order in orders" :key="order.serial" class="bg-gray-700 p-3 rounded shadow">
          <p><strong>Серийный номер:</strong> {{ order.serial }}</p>
          <p><strong>Название:</strong> {{ order.name }}</p>
          <p><strong>Заказчик:</strong> {{ order.customer }}</p>
          <p><strong>Приоритет:</strong> {{ order.priority ?? 'Н/Д' }}</p>
          <p><strong>Статус ID:</strong> {{ order.status_id }}</p>
          <p v-if="order.start_moment"><strong>Начало:</strong> {{ new Date(order.start_moment).toLocaleString() }}</p>
          <p v-if="order.deadline_moment"><strong>Дедлайн:</strong> {{ new Date(order.deadline_moment).toLocaleString() }}</p>
        </div>
      </div>
      <div v-else class="text-center text-gray-400 mt-5">
        Заказы по указанным критериям не найдены.
      </div>

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