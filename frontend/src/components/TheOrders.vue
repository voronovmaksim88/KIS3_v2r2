<!-- src/components/TheOrders.vue -->
<script setup lang="ts">
import {onMounted, ref} from 'vue';
import {storeToRefs} from 'pinia';
import {useOrdersStore} from '../stores/storeOrders';
import BaseButton from "@/components/Buttons/BaseButton.vue"; // Убедитесь, что путь к стору правильный
import TaskList from "@/components/TaskList.vue";
import {formatFIO} from "@/utils/formatFIO.ts";

// 1. Получаем экземпляр стора
const ordersStore = useOrdersStore();

// 2. Извлекаем реактивные переменные и действия из стора.
// Используем storeToRefs для сохранения реактивности состояния и вычисляемых свойств
const {
  orders,              // Список заказов для текущей страницы
  isLoading,           // Состояние загрузки (уже используется в шаблоне)
  error,               // Состояние ошибки (уже используется в шаблоне)
  totalOrders,         // Общее количество заказов
  currentPage,         // Текущая страница (вычисляемое)
  totalPages,          // Всего страниц (вычисляемое)
  currentLimit,        // Текущий лимит на странице
  currentSkip,         // Текущий пропуск записей
  currentOrderDetail,  // Данные о выбранном заказе
  isDetailLoading,     // Состояние загрузки деталей заказа
} = storeToRefs(ordersStore);

// Действия можно извлекать напрямую
const {fetchOrders, clearError, fetchOrderDetail, resetOrderDetail} = ordersStore;


function addNewOrder() {

}

function findOrders() {

}

// для хранения серийного номера заказа, чья дополнительная строка должна быть показана.
const expandedOrderSerial = ref<string | null>(null);

const toggleOrderDetails = async (serial: string) => {
  if (expandedOrderSerial.value === serial) {
    expandedOrderSerial.value = null;
    resetOrderDetail(); // Сбрасываем детали заказа
  } else {
    expandedOrderSerial.value = serial;
    // Просто вызываем fetchOrderDetail, данные сохранятся в сторе
    await fetchOrderDetail(serial);
  }
};


/**
 * Преобразует строку даты в формате ISO 8601 в локальную дату и время
 * @param isoDateString - Строка даты в формате ISO 8601 или null/undefined
 * @param includeHourAndMinute - Включать ли часы и минуты в результат (по умолчанию: true)
 * @param includeSeconds - Включать ли секунды в результат (по умолчанию: false)
 * @returns Отформатированная строка с локальными датой и временем
 */
function formatLocalDateTime(
    isoDateString: string | null | undefined,
    includeHourAndMinute: boolean = true,
    includeSeconds: boolean = false
): string {
  // Проверка на пустую строку или null/undefined
  if (!isoDateString) {
    return '';
  }

  try {
    // Создаем объект Date из строки ISO
    const date = new Date(isoDateString);

    // Проверяем, является ли дата валидной
    if (isNaN(date.getTime())) {
      console.error('Invalid date string:', isoDateString);
      return isoDateString; // Возвращаем исходную строку в случае ошибки
    }

    // Получаем разницу с UTC в часах для отображения
    const timezoneOffsetHours = -date.getTimezoneOffset() / 60;
    console.log(`Применено смещение часового пояса: UTC${timezoneOffsetHours >= 0 ? '+' : ''}${timezoneOffsetHours} часов`);

    // Прямое прибавление смещения часового пояса к времени
    // getTimezoneOffset возвращает смещение в минутах, отрицательное для восточных зон
    // поэтому мы вычитаем его, что эквивалентно прибавлению часов для восточных зон
    const adjustedDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);

    // Извлекаем компоненты даты напрямую (без toISOString)
    const year = adjustedDate.getFullYear();
    const month = String(adjustedDate.getMonth() + 1).padStart(2, '0');
    const day = String(adjustedDate.getDate()).padStart(2, '0');

    // Формируем строку с датой
    let formattedDate = `${year}-${month}-${day}`;

    // Добавляем часы и минуты, если необходимо
    if (includeHourAndMinute) {
      const hours = String(adjustedDate.getHours()).padStart(2, '0');
      const minutes = String(adjustedDate.getMinutes()).padStart(2, '0');
      formattedDate += ` ${hours}:${minutes}`;

      // Добавляем секунды, если они нужны и если включены часы/минуты
      if (includeSeconds) {
        const seconds = String(adjustedDate.getSeconds()).padStart(2, '0');
        formattedDate += `:${seconds}`;
      }
    }

    return formattedDate;
  } catch (error) {
    console.error('Error formatting date:', error);
    return isoDateString; // Возвращаем исходную строку в случае ошибки
  }
}


// Состояние для отображения завершенных заказов
const showEndedOrders = ref(true); // По умолчанию показываем все заказы

// Функция для переключения видимости завершенных заказов
const toggleEndedOrders = () => {
  // Вызов API с обновленным значением параметра showEnded
  fetchOrders({
    skip: 0, // Сбрасываем на первую страницу при смене фильтра
    limit: currentLimit.value,
    showEnded: showEndedOrders.value // Используем актуальное значение переключателя
  });
};


// Вызываем действие fetchOrders при монтировании компонента
onMounted(() => {
  // Загружаем первую страницу с учетом параметра showEndedOrders
  fetchOrders({skip: 0, limit: 20, showEnded: showEndedOrders.value});
});


// Функции для пагинации (вызывают fetchOrders с новыми параметрами)
const goToPreviousPage = () => {
  if (currentPage.value > 0) {
    const newSkip = currentSkip.value - currentLimit.value;
    fetchOrders({
      skip: newSkip,
      limit: currentLimit.value,
      showEnded: showEndedOrders.value // Добавляем параметр
    });
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    const newSkip = currentSkip.value + currentLimit.value;
    fetchOrders({
      skip: newSkip,
      limit: currentLimit.value,
      showEnded: showEndedOrders.value // Добавляем параметр
    });
  }
};

</script>


<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4 text-white">
    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <!-- Отображение ошибки -->
    <div
        v-if="!isLoading && error"
        class="w-full bg-red-500 text-white p-4 rounded mb-4 flex justify-between items-center"
    >
      <span>Ошибка: {{ error }}</span>
      <div>
        <button
            @click="fetchOrders({ skip: currentSkip, limit: currentLimit, showEnded: showEndedOrders })"
            class="ml-4 p-1 px-2 bg-red-700 rounded hover:bg-red-600 text-xs"
        >
          Повторить
        </button>
        <button
            @click="clearError"
            class="ml-2 p-1 px-2 bg-gray-600 rounded hover:bg-gray-500 text-xs"
        >
          Скрыть
        </button>
      </div>
    </div>

    <!-- Основной контент -->
    <div v-if="!isLoading && !error" class="w-full">
      <table class="min-w-full bg-gray-700 rounded-lg mb-4 table-fixed">
        <colgroup>
          <col style="width: 7%">  <!-- номер заказа -->
          <col style="width: 21%"> <!-- Заказчик -->
          <col style="width: 7%">  <!-- Приоритет -->
          <col style="width: 25%"> <!-- Название -->
          <col style="width: 15%"> <!-- Виды работ -->
          <col style="width: 25%"> <!-- Статус -->
        </colgroup>
        <thead>
        <tr>
          <th colspan="6" class="px-2 py-2 text-center bg-gray-600">
            <div class="px-1 py-1 bg-gray-600 flex justify-between items-center">
              <!-- Переключатель слева -->
              <span class="flex items-center">
                  <label for="toggle-ended-orders" class="flex items-center cursor-pointer">
                    <span class="relative">
                      <input
                          id="toggle-ended-orders"
                          type="checkbox"
                          v-model="showEndedOrders"
                          @change="toggleEndedOrders"
                          class="sr-only"
                      />
                      <span class="block bg-gray-700 w-10 h-6 rounded-full border border-gray-400"></span>
                      <span
                          class="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition"
                          :class="{ 'transform translate-x-4': showEndedOrders }"
                      ></span>
                    </span>
                    <span class="ml-3 text-gray-200 text-sm">
                      {{ showEndedOrders ? 'Скрыть завершённые' : 'Показать завершённые' }}
                    </span>
                  </label>
                </span>

              <!-- Кнопки справа -->
              <span class="flex">
                  <BaseButton
                      :action="addNewOrder"
                      :text="'Поиск'"
                      :style="'Primary'"
                      class="mr-2"
                  />
                  <BaseButton
                      :action="findOrders"
                      :text="'Добавить'"
                      :style="'Success'"
                  />
                </span>
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
        <template v-for="order in orders" :key="order.serial">
          <!-- Строка заказа -->
          <tr class="border-t border-gray-600">
            <td
                class="px-4 py-2 cursor-pointer hover:bg-gray-600 transition duration-300"
                :class="{
                  'font-bold': [1, 2, 3, 4, 8].includes(order.status_id),
                  'text-yellow-400': order.status_id === 1,
                  'text-blue-400': order.status_id === 2,
                  'text-green-400': order.status_id === 3,
                  'text-red-400': order.status_id === 4
                }"
                @click="toggleOrderDetails(order.serial)"
            >
              {{ order.serial }}
            </td>
            <td class="px-4 py-2">{{ order.customer }}</td>
            <td class="px-4 py-2">{{ order.priority ?? '-' }}</td>
            <td class="px-4 py-2">{{ order.name }}</td>
            <td class="px-4 py-2">
              <p v-for="work in order.works" :key="work.id">
                • {{ work.name }}
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

          <!-- Детали заказа -->
          <tr v-if="expandedOrderSerial === order.serial" class="border-b border-gray-600">
            <td colspan="6" class="p-4 bg-gray-700 text-gray-300">
              <!-- Индикатор загрузки деталей -->
              <div v-if="isDetailLoading" class="flex justify-center items-center p-4">
                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500 mr-2"></div>
                <span>Загрузка данных заказа...</span>
              </div>

              <!-- Отображение деталей заказа -->
              <div v-else>
                <div class="grid grid-cols-3 gap-4">
                  <!-- Комментарии -->
                  <div class="border rounded-md p-3 bg-gray-800 h-full">
                    <h4 class="font-semibold text-white mb-2">Комментарии</h4>
                    <div
                        v-if="!currentOrderDetail?.comments || currentOrderDetail.comments.length === 0"
                        class="text-gray-400"
                    >
                      Нет комментариев
                    </div>
                    <div v-else class="space-y-2">
                      <div
                          v-for="(comment, index) in currentOrderDetail.comments"
                          :key="index"
                          class="border rounded-md border-gray-700 p-2 mb-2"
                      >
                        <div class="flex justify-between items-center">
                          <div class="text-xs text-gray-400">
                            {{ formatLocalDateTime(comment.moment_of_creation) || 'Дата не указана' }}
                          </div>
                          <div class="text-xs text-gray-400">
                            {{ formatFIO(comment.person) || 'Автор не указан' }}
                          </div>
                        </div>
                        <div class="mt-1">{{ comment.text }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Даты и финансы -->
                  <div class="flex flex-col gap-4">
                    <!-- Даты -->
                    <div class="border rounded-md p-3 bg-gray-800">
                      <h4 class="font-semibold text-white mb-2">Даты</h4>
                      <p>
                        создан: {{ formatLocalDateTime(currentOrderDetail?.start_moment, false) || 'не определено' }}
                      </p>
                      <p>
                        дедлайн: {{ formatLocalDateTime(currentOrderDetail?.deadline_moment, false) || 'не определено' }}
                      </p>
                      <p v-if="currentOrderDetail?.end_moment">
                        завершен: {{ formatLocalDateTime(currentOrderDetail?.end_moment, false) || 'не определено' }}
                      </p>
                    </div>

                    <!-- Финансы -->
                    <div class="border rounded-md p-3 bg-gray-800">
                      <h4 class="font-semibold text-white mb-2">Финансы</h4>
                      <div class="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span>Материалы: </span>
                          <span
                              class="font-medium text-red-300"
                              :class="{ 'line-through opacity-60': currentOrderDetail?.materials_paid }"
                          >
                              {{ currentOrderDetail?.materials_cost }} руб.
                            </span>
                        </div>
                        <div>
                          <span>Товары: </span>
                          <span
                              class="font-medium text-red-300"
                              :class="{ 'line-through opacity-60': currentOrderDetail?.products_paid }"
                          >
                              {{ currentOrderDetail?.products_cost }} руб.
                            </span>
                        </div>
                        <div>
                          <span>Работы: </span>
                          <span
                              class="font-medium text-red-300"
                              :class="{ 'line-through opacity-60': currentOrderDetail?.work_paid }"
                          >
                              {{ currentOrderDetail?.work_cost }} руб.
                            </span>
                        </div>
                        <div>
                          <span>Нам должны: </span>
                          <span
                              class="font-medium text-green-400"
                              :class="{ 'line-through opacity-60': currentOrderDetail?.debt_paid }"
                          >
                              {{ currentOrderDetail?.debt }} руб.
                            </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Список задач -->
                  <div class="h-full">
                    <TaskList :tasks="currentOrderDetail?.tasks || []" />
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </template>
        </tbody>
      </table>

      <!-- Пагинация -->
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

      <!-- Информация о количестве заказов -->
      <div v-if="!isLoading && orders.length > 0" class="text-center text-gray-400 mt-2 text-sm">
        Показано {{ orders.length }} из {{ totalOrders }} заказов.
      </div>
    </div>
  </div>
</template>
<style scoped>
/* Можно добавить специфичные стили, если нужно */
</style>