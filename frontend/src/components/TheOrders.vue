<!-- src/components/TheOrders.vue -->
<script setup lang="ts">
import {onMounted, ref, computed} from 'vue';
import {storeToRefs} from 'pinia';
import {useOrdersStore} from '../stores/storeOrders';
import BaseButton from "@/components/Buttons/BaseButton.vue";
import TaskList from "@/components/TaskList.vue";
import {formatFIO} from "@/utils/formatFIO.ts";
import OrderCreateForm from '@/components/OrderCreateForm.vue'; // Импорт нашего нового компонента
import {useThemeStore} from '../stores/storeTheme';

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
const {fetchOrders, clearError, fetchOrderDetail, resetOrderDetail, resetOrders} = ordersStore;

// Состояние для модального окна создания заказа
const showCreateDialog = ref(false);


// Методы для управления прокруткой страницы
function disableScroll() {
  document.body.style.overflow = 'hidden';
}

function enableScroll() {
  document.body.style.overflow = '';
}

// Модифицируем функцию addNewOrder
function addNewOrder() {
  showCreateDialog.value = true;
  disableScroll(); // Блокируем прокрутку при открытии модального окна
}

// Модифицируем обработчики закрытия модального окна
const handleOrderCreated = () => {
  showCreateDialog.value = false;
  enableScroll(); // Восстанавливаем прокрутку при закрытии модального окна
  // обновляем список заказов после успешного создания
  fetchOrders({
    skip: currentSkip.value,
    limit: currentLimit.value,
    showEnded: showEndedOrders.value
  });
}

const handleCreateCancel = () => {
  showCreateDialog.value = false;
  enableScroll(); // Восстанавливаем прокрутку при закрытии модального окна
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
  // Сбрасываем список заказов
  resetOrders()

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


// Классы для заголовков таблицы (<th>)
const thClasses = computed(() => {
  const base = 'px-4 py-2 text-left text-sm font-semibold uppercase tracking-wider'; // Общие стили
  if (currentTheme.value === 'dark') {
    return `${base} border-1 border-gray-300 text-gray-300 bg-gray-600`; // Стили для темной темы
  } else {
    return `${base} border-1 border-gray-300 text-gray-600 bg-gray-100`; // Стили для светлой темы
  }
});

// Базовый цвет текста для обычных ячеек таблицы (<td>)
const tdBaseTextClass = computed(() => {
  return currentTheme.value === 'dark' ? 'text-gray-100' : 'text-gray-800';
});

// Классы для контейнера раскрытых деталей (<td> colspan="6")
const detailsContainerClass = computed(() => {
  const base = 'p-4 transition-colors duration-300 ease-in-out';
  return currentTheme.value === 'dark'
      ? `${base} bg-gray-750 text-gray-300` // Используем bg-gray-750 для отличия
      : `${base} bg-gray-50 text-gray-700`; // Используем bg-gray-50 для отличия
});

// Классы для основных блоков внутри деталей (Комментарии, Даты, Финансы, Задачи)
const detailBlockClass = computed(() => {
  const base = 'border rounded-md p-3 h-full transition-colors duration-300 ease-in-out';
  return currentTheme.value === 'dark'
      ? `${base} bg-gray-800 border-gray-600`
      : `${base} bg-white border-gray-200 shadow-sm`;
});

// Классы для заголовков (<h4>) внутри блоков деталей
const detailHeaderClass = computed(() => {
  const base = 'font-semibold mb-2';
  return currentTheme.value === 'dark'
      ? `${base} text-white`
      : `${base} text-gray-800`;
});

// Классы для второстепенного текста (даты/авторы комментариев, "Нет комментариев")
const detailSubtleTextClass = computed(() => {
  return currentTheme.value === 'dark' ? 'text-gray-400' : 'text-gray-500';
});

// Классы для отдельного комментария
const commentItemClass = computed(() => {
  const base = 'border rounded-md p-2 mb-2 transition-colors duration-300 ease-in-out';
  // Используем bg-gray-850/bg-gray-100 для отличия от фона блока
  return currentTheme.value === 'dark'
      ? `${base} border-gray-700 bg-gray-850`
      : `${base} border-gray-300 bg-gray-100`;
});

// Классы для кнопок пагинации
const paginationButtonClass = computed(() => {
  const base = 'px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300';
  return currentTheme.value === 'dark'
      ? `${base} bg-blue-600 hover:bg-blue-500 text-white`
      : `${base} bg-blue-500 hover:bg-blue-600 text-white`;
});

// Классы для текста пагинации
const paginationTextClass = computed(() => {
  const base = 'text-lg transition-colors duration-300';
  return currentTheme.value === 'dark' ? `${base} text-gray-300` : `${base} text-gray-700`;
});

// Классы для текста "Показано N из M заказов"
const totalInfoTextClass = computed(() => {
  const base = 'text-center mt-2 text-sm transition-colors duration-300';
  return currentTheme.value === 'dark' ? `${base} text-gray-400` : `${base} text-gray-500`;
});

// Классы для основного контейнера компонента
const mainContainerClass = computed(() => {
  const base = 'w-full min-h-screen flex flex-col items-center p-4 transition-colors duration-300 ease-in-out';
  // Используем bg-gray-900 для темной темы для лучшего контраста с таблицей bg-gray-700
  return currentTheme.value === 'dark' ? `${base} bg-gray-900 text-gray-100` : `${base} bg-gray-100 text-gray-900`;
});

// Классы для фона основной таблицы
const tableBaseClass = computed(() => {
  const base = 'min-w-full rounded-lg mb-4 table-fixed shadow-md';
  return currentTheme.value === 'dark' ? `${base} bg-gray-700` : `${base} bg-white border border-gray-200`;
});

// Классы для шапки таблицы (<th> colspan=6)
const tableHeaderRowClass = computed(() => {
  const base = 'px-2 py-2 text-center rounded-t-lg';
  return currentTheme.value === 'dark' ? `${base} bg-gray-600` : `${base} bg-gray-200`;
});

// Классы для фона переключателя
const toggleBackgroundClass = computed(() => {
  const base = 'block w-10 h-6 rounded-full border transition-colors duration-300';
  return currentTheme.value === 'dark' ? `${base} bg-gray-800 border-gray-500` : `${base} bg-gray-300 border-gray-400`;
});

// Классы для текста переключателя
const toggleTextClass = computed(() => {
  const base = 'ml-3 text-sm transition-colors duration-300';
  return currentTheme.value === 'dark' ? `${base} text-gray-200` : `${base} text-gray-700`;
});

// Классы для строки таблицы (<tr>)
const trBaseClass = computed(() => {
  const base = 'transition-colors duration-100';
  return currentTheme.value === 'dark' ? `${base} border-t border-gray-600` : `${base} border-t border-gray-200`;
});

// Классы для hover эффекта ячейки с номером
const tdNumberHoverClass = computed(() => {
  return currentTheme.value === 'dark' ? 'hover:bg-gray-600' : 'hover:bg-gray-100';
});

// Классы для блока ошибки
const errorBlockClass = computed(() => {
  const base = 'w-full p-4 rounded mb-4 flex justify-between items-center transition-colors duration-300 ease-in-out';
  return currentTheme.value === 'dark' ? `${base} bg-red-800 text-red-100` : `${base} bg-red-100 text-red-800 border border-red-300`;
});

// Классы для кнопки "Повторить" в ошибке
const errorRepeatButtonClass = computed(() => {
  const base = 'ml-4 p-1 px-2 rounded text-xs transition-colors duration-300';
  return currentTheme.value === 'dark' ? `${base} bg-red-600 hover:bg-red-500 text-white` : `${base} bg-red-500 hover:bg-red-600 text-white`;
});

// Классы для кнопки "Скрыть" в ошибке
const errorHideButtonClass = computed(() => {
  const base = 'ml-2 p-1 px-2 rounded text-xs transition-colors duration-300';
  return currentTheme.value === 'dark' ? `${base} bg-gray-600 hover:bg-gray-500 text-white` : `${base} bg-gray-300 hover:bg-gray-400 text-gray-800`;
});

</script>



<template>
  <div :class="mainContainerClass">



    <!-- Модальное окно создания заказа -->
    <transition name="fade">
      <div v-if="showCreateDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="max-w-4xl w-full">
          <OrderCreateForm
              @success="handleOrderCreated"
              @cancel="handleCreateCancel"
          />
        </div>
      </div>
    </transition>

    <div v-if="isLoading && orders.length === 0" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>


    <div v-if="!isLoading && error" :class="errorBlockClass">
      <span>Ошибка: {{ error }}</span>
      <div>
        <button
            @click="fetchOrders({ skip: currentSkip, limit: currentLimit, showEnded: showEndedOrders })"
            :class="errorRepeatButtonClass"
        >
          Повторить
        </button>
        <button
            @click="clearError"
            :class="errorHideButtonClass"
        >
          Скрыть
        </button>
      </div>
    </div>


    <div v-if="(!isLoading && !error) || (isLoading && orders.length > 0)" class="w-full">
      <table :class="tableBaseClass">
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
          <th colspan="6" :class="tableHeaderRowClass">
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

                      <span :class="toggleBackgroundClass"></span>

                      <span
                          class="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition"
                          :class="{ 'transform translate-x-4': showEndedOrders }"
                      ></span>
                    </span>

                    <span :class="toggleTextClass">
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

          <th :class="thClasses">Номер</th>
          <th :class="thClasses">Заказчик</th>
          <th :class="thClasses">Приоритет</th>
          <th :class="thClasses">Название</th>
          <th :class="thClasses">Виды работ</th>
          <th :class="thClasses">Статус</th>
        </tr>
        </thead>
        <tbody>
        <template v-for="order in orders" :key="order.serial">

          <tr :class="trBaseClass">

            <td
                class="px-4 py-2 cursor-pointer transition duration-300"
                :class="[
                  tdNumberHoverClass, // computed для hover
                  tdBaseTextClass, // computed для базового текста
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


            <td class="px-4 py-2" :class="tdBaseTextClass"> {{ order.customer }}</td>
            <td class="px-4 py-2" :class="tdBaseTextClass"> {{ order.priority ?? '-' }}</td>
            <td class="px-4 py-2" :class="tdBaseTextClass"> {{ order.name }}</td>
            <td class="px-4 py-2" :class="tdBaseTextClass">
              <p v-for="work in order.works" :key="work.id"> • {{ work.name }} </p>
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
            <td colspan="6" :class="detailsContainerClass">

              <div v-if="isDetailLoading" class="flex justify-center items-center p-4">
                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500 mr-2"></div>
                <span>Загрузка данных заказа...</span>
              </div>


              <div v-else>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

                  <div :class="detailBlockClass">
                    <h4 :class="detailHeaderClass">Комментарии</h4>
                    <div
                        v-if="!currentOrderDetail?.comments || currentOrderDetail.comments.length === 0"
                        :class="detailSubtleTextClass"
                    >
                      Нет комментариев
                    </div>
                    <div v-else class="space-y-2">
                      <div
                          v-for="(comment, index) in currentOrderDetail.comments"
                          :key="index"
                          :class="commentItemClass"
                      >
                        <div class="flex justify-between items-center">
                          <div class="text-xs" :class="detailSubtleTextClass">
                            {{ formatLocalDateTime(comment.moment_of_creation) || 'Дата не указана' }}
                          </div>
                          <div class="text-xs" :class="detailSubtleTextClass">
                            {{ formatFIO(comment.person) || 'Автор не указан' }}
                          </div>
                        </div>
                        <div class="mt-1" :class="tdBaseTextClass">{{ comment.text }}</div>
                      </div>
                    </div>
                  </div>


                  <div class="flex flex-col gap-4">

                    <div :class="detailBlockClass">
                      <h4 :class="detailHeaderClass">Даты</h4>
                      <p :class="tdBaseTextClass">
                        создан: {{ formatLocalDateTime(currentOrderDetail?.start_moment, false) || 'не определено' }}
                      </p>
                      <p :class="tdBaseTextClass">
                        дедлайн: {{
                          formatLocalDateTime(currentOrderDetail?.deadline_moment, false) || 'не определено'
                        }}
                      </p>
                      <p v-if="currentOrderDetail?.end_moment" :class="tdBaseTextClass">
                        завершен: {{ formatLocalDateTime(currentOrderDetail?.end_moment, false) || 'не определено' }}
                      </p>
                    </div>


                    <div :class="detailBlockClass">
                      <h4 :class="detailHeaderClass">Финансы</h4>

                      <div class="grid grid-cols-2 gap-2 text-sm" :class="tdBaseTextClass">
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

                  <TaskList :tasks="currentOrderDetail?.tasks || []" :theme="currentTheme"/>

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
            :class="paginationButtonClass"
        >
          Назад
        </button>
        <span :class="paginationTextClass">
          Страница {{ currentPage + 1 }} из {{ totalPages }}
        </span>
        <button
            @click="goToNextPage"
            :disabled="currentPage >= totalPages - 1"
            :class="paginationButtonClass"
        >
          Вперед
        </button>
      </div>


      <div v-if="!isLoading && orders.length > 0" :class="totalInfoTextClass">
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
  transform: translateX(1rem); /* 16px, что равно w-4 */
}

/* Добавляем плавный переход для точки */
.dot {
  transition: transform 0.3s ease-in-out;
}

/* Добавляем стили для модального окна PrimeVue Dialog с использованием v-bind */
:deep(.p-dialog) {
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
  /* Динамическая рамка для светлой темы */
  border: 1px solid v-bind('currentTheme === "dark" ? "transparent" : "rgba(209, 213, 219, 1)"'); /* border-gray-300 */
  /* Тень для светлой темы */
  box-shadow: v-bind('currentTheme === "dark" ? "none" : "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"');
}


</style>