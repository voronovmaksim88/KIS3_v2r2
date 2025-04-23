<!-- src/components/TheOrders.vue -->
<script setup lang="ts">
import {onMounted, ref} from 'vue';
import {storeToRefs} from 'pinia';
import {useOrdersStore} from '../stores/storeOrders';
import BaseButton from "@/components/Buttons/BaseButton.vue";
import TaskList from "@/components/TaskList.vue";
import {formatFIO} from "@/utils/formatFIO.ts";
import Dialog from 'primevue/dialog'; // Импорт Dialog из PrimeVue
import OrderCreateForm from '@/components/OrderCreateForm.vue'; // Импорт нашего нового компонента
import {useThemeStore} from '../stores/storeTheme'; // <--- 1. Импорт Theme Store

// Store темы
const themeStore = useThemeStore(); // <--- 2. Получаем экземпляр Theme Store
const {theme: currentTheme} = storeToRefs(themeStore); // <--- 3. Получаем реактивную ссылку на тему

// 1. Получаем экземпляр стора
const ordersStore = useOrdersStore();

// 2. Извлекаем реактивные переменные и действия из стора.
const {
  orders,
  isLoading,
  error,
  totalOrders,
  currentPage,
  totalPages,
  currentLimit,
  currentSkip,
  currentOrderDetail,
  isDetailLoading,
} = storeToRefs(ordersStore);

// Действия можно извлекать напрямую
const {fetchOrders, clearError, fetchOrderDetail, resetOrderDetail} = ordersStore;

// Состояние для модального окна создания заказа
const showCreateDialog = ref(false);

function addNewOrder() {
  showCreateDialog.value = true;
}

// Обработчик успешного создания заказа
const handleOrderCreated = () => {
  showCreateDialog.value = false;
  // Обновляем список заказов после успешного создания
  fetchOrders({
    skip: currentSkip.value,
    limit: currentLimit.value,
    showEnded: showEndedOrders.value
  });
}

// Обработчик отмены создания заказа
const handleCreateCancel = () => {
  showCreateDialog.value = false;
}

function findOrders() {
  // Функциональность поиска может быть добавлена позже
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
const showEndedOrders = ref(false); // По умолчанию скрываем завершённые заказы

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
  fetchOrders({skip: 0, limit: 50, showEnded: showEndedOrders.value});
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
  <div
      class="w-full min-h-screen flex flex-col items-center p-4 transition-colors duration-300 ease-in-out"
      :class="[ currentTheme === 'dark' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900' ]"
  >


    <Dialog
        v-model:visible="showCreateDialog"
        modal
        :style="{width: '500px'}"
        :closable="false"
        class="p-0"
        :draggable="false"
    >

      <OrderCreateForm
          @success="handleOrderCreated"
          @cancel="handleCreateCancel"
      />
    </Dialog>


    <div v-if="isLoading" class="w-full flex justify-center my-4">

      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>


    <div
        v-if="!isLoading && error"
        class="w-full p-4 rounded mb-4 flex justify-between items-center transition-colors duration-300 ease-in-out"
        :class="[ currentTheme === 'dark' ? 'bg-red-800 text-red-100' : 'bg-red-100 text-red-800 border border-red-300' ]"
    >
      <span>Ошибка: {{ error }}</span>
      <div>

        <button
            @click="fetchOrders({ skip: currentSkip, limit: currentLimit, showEnded: showEndedOrders })"
            class="ml-4 p-1 px-2 rounded text-xs transition-colors duration-300"
            :class="[ currentTheme === 'dark' ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-red-500 hover:bg-red-600 text-white' ]"
        >
          Повторить
        </button>
        <button
            @click="clearError"
            class="ml-2 p-1 px-2 rounded text-xs transition-colors duration-300"
            :class="[ currentTheme === 'dark' ? 'bg-gray-600 hover:bg-gray-500 text-white' : 'bg-gray-300 hover:bg-gray-400 text-gray-800' ]"
        >
          Скрыть
        </button>
      </div>
    </div>


    <div v-if="!isLoading && !error" class="w-full">
      <table
          class="min-w-full rounded-lg mb-4 table-fixed shadow-md"
          :class="[ currentTheme === 'dark' ? 'bg-gray-700' : 'bg-white border border-gray-200' ]"
      >
        <colgroup>
          <col style="width: 7%">
          <col style="width: 21%">
          <col style="width: 7%">
          <col style="width: 25%">
          <col style="width: 15%">
          <col style="width: 25%">
        </colgroup>
        <thead>
        <tr>
          <th
              colspan="6"
              class="px-2 py-2 text-center rounded-t-lg"
              :class="[ currentTheme === 'dark' ? 'bg-gray-600' : 'bg-gray-200' ]"
          >
            <div class="px-1 py-1 flex justify-between items-center">
              
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
                      
                      <span
                          class="block w-10 h-6 rounded-full border transition-colors duration-300"
                          :class="[ currentTheme === 'dark' ? 'bg-gray-800 border-gray-500' : 'bg-gray-300 border-gray-400' ]"
                      ></span>
                      
                      <span
                          class="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition"
                          :class="{ 'transform translate-x-4': showEndedOrders }"
                      ></span>
                    </span>
                    
                    <span
                        class="ml-3 text-sm transition-colors duration-300"
                        :class="[ currentTheme === 'dark' ? 'text-gray-200' : 'text-gray-700' ]"
                    >
                      {{ showEndedOrders ? 'Скрыть завершённые' : 'Показать завершённые' }}
                    </span>
                  </label>
                </span>


              <span class="flex">
                  <BaseButton
                      :action="findOrders"
                      :text="'Поиск'"
                      :style="'Primary'"
                      class="mr-2"
                  />
                  <BaseButton
                      :action="addNewOrder"
                      :text="'Добавить'"
                      :style="'Success'"
                  />
                </span>
            </div>
          </th>
        </tr>
        <tr>

          <th
              class="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider border-1"
              :class="[ currentTheme === 'dark' ? 'border-gray-300 text-gray-300' : ' border-gray-600 text-gray-600 bg-gray-100' ]"
          >Номер
          </th>
          <th
              class="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider border-1"
              :class="[ currentTheme === 'dark' ? 'border-gray-300 text-gray-300' : ' border-gray-600 text-gray-600 bg-gray-100' ]"
          >Заказчик
          </th>
          <th
              class="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider"
              :class="[ currentTheme === 'dark' ? 'border-gray-300 text-gray-300' : ' border-gray-600 text-gray-600 bg-gray-100' ]"
          >Приоритет
          </th>
          <th
              class="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider border-1"
              :class="[ currentTheme === 'dark' ? 'border-gray-300 text-gray-300' : ' border-gray-600 text-gray-600 bg-gray-100' ]"
          >Название
          </th>
          <th
              class="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider border-1"
              :class="[ currentTheme === 'dark' ? 'border-gray-300 text-gray-300' : ' border-gray-600 text-gray-600 bg-gray-100' ]"
          >Виды работ
          </th>
          <th
              class="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider border-1"
              :class="[ currentTheme === 'dark' ? 'border-gray-300 text-gray-300' : ' border-gray-600 text-gray-600 bg-gray-100' ]"
          >Статус
          </th>
        </tr>
        </thead>
        <tbody>
        <template v-for="order in orders" :key="order.serial">

          <tr
              class="transition-colors duration-100"
              :class="[ currentTheme === 'dark' ? 'border-t border-gray-600' : 'border-t border-gray-200' ]"
          >

            <td
                class="px-4 py-2 cursor-pointer transition duration-300"
                :class="[
                  currentTheme === 'dark' ? 'hover:bg-gray-600' : 'hover:bg-gray-100',
                  {
                    'font-bold': [1, 2, 3, 4, 8].includes(order.status_id),
                    'text-yellow-400': order.status_id === 1, // Статусные цвета остаются
                    'text-blue-400': order.status_id === 2,
                    'text-green-400': order.status_id === 3,
                    'text-red-400': order.status_id === 4
                  }
                ]"
                @click="toggleOrderDetails(order.serial)"
            >
              {{ order.serial }}
            </td>


            <td
                class="px-4 py-2"
                :class="[ currentTheme === 'dark' ? 'text-gray-100' : 'text-gray-800' ]"
            >
              {{ order.customer }}
            </td>


            <td
                class="px-4 py-2"
                :class="[ currentTheme === 'dark' ? 'text-gray-100' : 'text-gray-800' ]"
            >
              {{ order.priority ?? '-' }}
            </td>


            <td
                class="px-4 py-2"
                :class="[ currentTheme === 'dark' ? 'text-gray-100' : 'text-gray-800' ]"
            >
              {{ order.name }}
            </td>


            <td
                class="px-4 py-2"
                :class="[ currentTheme === 'dark' ? 'text-gray-100' : 'text-gray-800' ]"
            >
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


          <tr
              v-if="expandedOrderSerial === order.serial"
              :class="[ currentTheme === 'dark' ? 'border-b border-gray-600' : 'border-b border-gray-200' ]"
          >
            <td
                colspan="6"
                class="p-4 transition-colors duration-300 ease-in-out"
                :class="[ currentTheme === 'dark' ? 'bg-gray-750 text-gray-300' : 'bg-gray-50 text-gray-700' ]"
            >

              <div v-if="isDetailLoading" class="flex justify-center items-center p-4">
                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500 mr-2"></div>
                <span>Загрузка данных заказа...</span>
              </div>


              <div v-else>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

                  <div
                      class="border rounded-md p-3 h-full transition-colors duration-300 ease-in-out"
                      :class="[ currentTheme === 'dark' ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200 shadow-sm' ]"
                  >
                    <h4
                        class="font-semibold mb-2"
                        :class="[ currentTheme === 'dark' ? 'text-white' : 'text-gray-800' ]"
                    >Комментарии</h4>
                    <div
                        v-if="!currentOrderDetail?.comments || currentOrderDetail.comments.length === 0"
                        :class="[ currentTheme === 'dark' ? 'text-gray-400' : 'text-gray-500' ]"
                    >
                      Нет комментариев
                    </div>
                    <div v-else class="space-y-2">
                      <div
                          v-for="(comment, index) in currentOrderDetail.comments"
                          :key="index"
                          class="border rounded-md p-2 mb-2 transition-colors duration-300 ease-in-out"
                          :class="[ currentTheme === 'dark' ? 'border-gray-700 bg-gray-800' : 'border-gray-300 bg-gray-100' ]"
                      >
                        <div class="flex justify-between items-center">
                          <div class="text-xs" :class="[ currentTheme === 'dark' ? 'text-gray-400' : 'text-gray-500' ]">
                            {{ formatLocalDateTime(comment.moment_of_creation) || 'Дата не указана' }}
                          </div>
                          <div class="text-xs" :class="[ currentTheme === 'dark' ? 'text-gray-400' : 'text-gray-500' ]">
                            {{ formatFIO(comment.person) || 'Автор не указан' }}
                          </div>
                        </div>
                        <div class="mt-1">{{ comment.text }}</div>
                      </div>
                    </div>
                  </div>


                  <div class="flex flex-col gap-4">

                    <div
                        class="border rounded-md p-3 transition-colors duration-300 ease-in-out"
                        :class="[ currentTheme === 'dark' ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200 shadow-sm' ]"
                    >
                      <h4
                          class="font-semibold mb-2"
                          :class="[ currentTheme === 'dark' ? 'text-white' : 'text-gray-800' ]"
                      >Даты</h4>
                      <p>
                        создан: {{ formatLocalDateTime(currentOrderDetail?.start_moment, false) || 'не определено' }}
                      </p>
                      <p>
                        дедлайн: {{
                          formatLocalDateTime(currentOrderDetail?.deadline_moment, false) || 'не определено'
                        }}
                      </p>
                      <p v-if="currentOrderDetail?.end_moment">
                        завершен: {{ formatLocalDateTime(currentOrderDetail?.end_moment, false) || 'не определено' }}
                      </p>
                    </div>


                    <div
                        class="border rounded-md p-3 transition-colors duration-300 ease-in-out"
                        :class="[ currentTheme === 'dark' ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200 shadow-sm' ]"
                    >
                      <h4
                          class="font-semibold mb-2"
                          :class="[ currentTheme === 'dark' ? 'text-white' : 'text-gray-800' ]"
                      >Финансы</h4>
                      {/* Цвета сумм (красный/зеленый) не зависят от темы */}
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


                  <div
                      class="h-full border rounded-md p-1 transition-colors duration-300 ease-in-out"
                      :class="[ currentTheme === 'dark' ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200 shadow-sm' ]"
                  >
                    <h4
                        class="font-semibold mb-2 px-2 pt-2"
                        :class="[ currentTheme === 'dark' ? 'text-white' : 'text-gray-800' ]"
                    >Задачи</h4>
                    <TaskList :tasks="currentOrderDetail?.tasks || []"/>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </template>
        </tbody>
      </table>


      <div v-if="totalPages > 1" class="mt-6 flex justify-center items-center space-x-3">
        <button
            @click="goToPreviousPage"
            :disabled="currentPage === 0"
            class="px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300"
            :class="[ currentTheme === 'dark' ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white' ]"
        >
          Назад
        </button>
        <span
            class="text-lg transition-colors duration-300"
            :class="[ currentTheme === 'dark' ? 'text-gray-300' : 'text-gray-700' ]"
        >
          Страница {{ currentPage + 1 }} из {{ totalPages }}
        </span>
        <button
            @click="goToNextPage"
            :disabled="currentPage >= totalPages - 1"
            class="px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300"
            :class="[ currentTheme === 'dark' ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white' ]"
        >
          Вперед
        </button>
      </div>


      <div
          v-if="!isLoading && orders.length > 0"
          class="text-center mt-2 text-sm transition-colors duration-300"
          :class="[ currentTheme === 'dark' ? 'text-gray-400' : 'text-gray-500' ]"
      >
        Показано {{ orders.length }} из {{ totalOrders }} заказов.
      </div>
    </div>
  </div>

  <!-- Элемент, который формально использует классы для успокоения линтера.
     Он не отображается, так как имеет display: none; -->
  <div
      v-if="false"
      class="p-dialog p-dialog-header p-dialog-content p-dialog-header-close"
      style="display: none;"
  ></div>
</template>

<style scoped>
/* Стили для переключателя */
/* Движение точки при checked */
input:checked ~ .dot {
  /* transform: translateX(100%); Это двигает на всю ширину контейнера span, нам нужно на ширину самой точки */
  transform: translateX(1rem); /* 16px, что равно w-4 */
  /* background-color: white; /* Точка всегда белая */
}

/* Добавляем плавный переход для точки */
.dot {
  transition: transform 0.3s ease-in-out;
}

/* Добавляем стили для модального окна PrimeVue Dialog с использованием v-bind */
:deep(.p-dialog) {
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease-in-out;
  /* Динамическая рамка для светлой темы */
  border: 1px solid v-bind('currentTheme === "dark" ? "transparent" : "rgba(209, 213, 219, 1)"');
  /* Можно добавить тень для светлой темы */
  box-shadow: v-bind('currentTheme === "dark" ? "none" : "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"');
}

</style>
