<!-- src/components/TheOrders.vue -->
<script setup lang="ts">
import {onMounted, ref, computed} from 'vue';
import {storeToRefs} from 'pinia';
import {useOrdersStore} from '../stores/storeOrders';
import {getStatusColor} from "@/utils/getStatusColor";

// импорт сторов
import {useThemeStore} from '../stores/storeTheme';
import {useCounterpartyStore} from '@/stores/storeCounterparty'; // Импортируем store контрагентов
import { useWorksStore } from "@/stores/storeWorks"; // <-- Импорт works store если еще не импортирован

// мои компоненты
import OrderCreateForm from '@/components/OrderCreateForm.vue'; // Импорт нашего нового компонента
import CommentBlock from '@/components/CommentBlock.vue';
import TaskList from "@/components/TaskList.vue";
import FinanceBlock from '@/components/FinanceBlock.vue';
import DateBlock from '@/components/DateBlock.vue';
import OrderNameEditDialog from '@/components/OrderNameEditDialog.vue'; // Импорт нового компонента диалога
import OrderWorksEditDialog from '@/components/OrderWorksEditDialog.vue'; // <-- Импорт нового компонента




// primevue компоненты
import Toast from 'primevue/toast'
import SelectButton from 'primevue/selectbutton';
import Select from 'primevue/select'; // Импортируем компонент выпадающего списка
import {useToast} from 'primevue/usetoast';
import Button from "primevue/button";


const toast = useToast();


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

// для сортировки
const {currentSortField, currentSortDirection} = storeToRefs(ordersStore);

// Добавляем store контрагентов
const counterpartyStore = useCounterpartyStore();

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


// Функция загрузки с автоповтором при ошибке 500
async function fetchOrdersWithRetry(params: { skip: number, limit: number, showEnded: boolean }) {
  try {
    await fetchOrders(params);
    // Если успешно, просто возвращаем
  } catch (err: any) {
    // Если ошибка есть и это 500, пробуем ещё раз
    if (err?.response?.status === 500 || (typeof error.value === 'string' && error.value.includes('500'))) {
      // Сбросить ошибку перед повтором (если нужно)
      clearError();
      try {
        await fetchOrders(params);
        // Если второй раз успешно — ок
      } catch {
        // Если второй раз ошибка — позволяем ошибке отобразиться
      }
    }
    // Если другая ошибка — ничего не делаем (она отобразится стандартно)
  }
}


// Вызываем действие fetchOrders при монтировании компонента
onMounted(() => {
  // Сбрасываем список заказов
  resetOrders()

  // Загружаем первую страницу с учетом параметра showEndedOrders
  //fetchOrders({skip: 0, limit: 50, showEnded: showEndedOrders.value});

  // Загружаем список контрагентов
  counterpartyStore.fetchCounterparties();

  // Загружаем работы один раз при монтировании основного компонента
  worksStore.fetchWorks();

  // Загружаем с повтором
  fetchOrdersWithRetry({skip: 0, limit: 50, showEnded: showEndedOrders.value});
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


// Функция для определения иконки сортировки
const getSortIcon = (field: string) => {
  if (currentSortField.value === field) {
    return currentSortDirection.value === 'asc' ? 'pi pi-sort-up' : 'pi pi-sort-down';
  }
  return 'pi pi-sort text-gray-400';
};

// Опции для переключателя видимости заказов
const orderVisibilityOptions = [
  {label: 'Активные', value: false},
  {label: 'Все заказы', value: true}
];


/**
 * Обработчик изменения заказчика заказа
 * @param orderId - ID заказа
 * @param customerId - ID нового заказчика
 */
const handleCustomerChange = async (orderId: string, customerId: number) => {
  try {
    console.log(`Заказчик для заказа ${orderId} изменен на ${customerId}`);

    // Используем существующий метод updateOrder, передавая только изменение customer_id
    await ordersStore.updateOrder(orderId, {customer_id: customerId});

    // Показываем уведомление об успехе через PrimeVue Toast
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Заказчик заказа #${orderId} успешно изменен`,
      life: 3000
    });
  } catch (error) {
    console.error('Ошибка при изменении заказчика:', error);
    // Показываем уведомление об ошибке
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Не удалось изменить заказчика заказа #${orderId}`,
      life: 5000
    });
  }
};


/**
 * Обработчик изменения приоритета заказа
 * @param orderId - ID заказа
 * @param priority - Новый приоритет
 */
const handlePriorityChange = async (orderId: string, priority: number | null) => {
  try {
    console.log(`Приоритет для заказа ${orderId} изменен на ${priority}`);

    // Используем существующий метод updateOrder
    await ordersStore.updateOrder(orderId, {priority});

    // Показываем уведомление об успехе через PrimeVue Toast
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Приоритет заказа #${orderId} успешно изменен`,
      life: 3000
    });
  } catch (error) {
    console.error('Ошибка при изменении приоритета:', error);
    // Показываем уведомление об ошибке
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Не удалось изменить приоритет заказа #${orderId}`,
      life: 5000
    });
  }
};


// Функция для получения опций для выпадающего списка контрагентов
const getCustomerOptions = computed(() => {
  return counterpartyStore.sortedCounterparties.map(cp => ({
    name: counterpartyStore.getFullName(cp),
    value: cp.id,
    code: cp.id.toString()
  }));
});

// Вспомогательная функция для получения имени по ID
const getCustomerNameById = (id: number): string => {
  const customer = counterpartyStore.getCounterpartyById(id);
  return customer ? counterpartyStore.getFullName(customer) : 'Заказчик не найден';
};

// Опции для приоритета
const priorityOptions = [
  {label: 'Нет', value: null},
  ...Array.from({length: 10}, (_, i) => ({
    label: (i + 1).toString(),
    value: i + 1,
  }))
];


// Состояние для диалога изменения названия
const showNameEditDialog = ref(false); // Оставить эту строку
const selectedOrderForNameEdit = ref<{ id: string | null, name: string }>({id: null, name: ''}); // Изменить тип и инициализацию

/**
 + * Открывает диалог изменения названия заказа
 + * @param orderId - ID заказа
 + * @param currentName - Текущее название заказа
 + */
const openNameEditDialog = (orderId: string, currentName: string) => {
  selectedOrderForNameEdit.value = {id: orderId, name: currentName};
  showNameEditDialog.value = true;
};


/**
 * Обработчик успешного обновления названия заказа из диалога
 */
const handleNameUpdated = async () => {
  // Здесь уже не нужно вызывать ordersStore.updateOrder или показывать toast,
  // так как это делает OrderNameEditDialog.
  // Но нужно обновить список заказов, чтобы изменения отобразились.
  await fetchOrders({
    skip: currentSkip.value,
    limit: currentLimit.value,
    showEnded: showEndedOrders.value
  });
  // Очищаем выбранный заказ после закрытия диалога
  selectedOrderForNameEdit.value = {id: null, name: ''};
};

// Обработчик отмены редактирования названия
const handleNameEditCancel = () => {
  selectedOrderForNameEdit.value = {id: null, name: ''};
};


// --- State for Works Edit Dialog ---
const showWorksEditDialog = ref(false);
const selectedOrderForWorksEdit = ref<{ id: string | null, workIds: number[] }>({ id: null, workIds: [] });
const worksStore = useWorksStore(); // <-- Получаем экземпляр works store


/**
 * Открывает диалог редактирования списка работ для заказа
 * @param orderId - ID заказа
 * @param currentWorks - Массив объектов текущих работ [{id: number, name: string}, ...]
 */
const openWorksEditDialog = (orderId: string, currentWorks: { id: number, name?: string }[]) => {
  selectedOrderForWorksEdit.value = {
    id: orderId,
    workIds: currentWorks ? currentWorks.map(w => w.id) : [] // Извлекаем только ID
  };
  // Предзагрузка списка работ, если он пуст (проверяем основной массив 'works')
  // Это запасной вариант, так как fetchWorks вызывается в onMounted
  if (worksStore.works.length === 0 && !worksStore.isLoading) { // <--- FIX HERE
    worksStore.fetchWorks();
  }
  showWorksEditDialog.value = true;
  disableScroll(); // Блокируем прокрутку
};



/**
 * Обработчик успешного обновления списка работ из диалога
 */
const handleWorksUpdated = async () => {
  // Просто обновим список заказов, чтобы увидеть изменения
  // В будущем можно оптимизировать и обновить только измененный заказ локально
  await fetchOrders({
    skip: currentSkip.value,
    limit: currentLimit.value,
    showEnded: showEndedOrders.value
  });
  enableScroll(); // Восстанавливаем прокрутку
};

// Обработчик отмены редактирования списка работ
const handleWorksEditCancel = () => {
  // selectedOrderForWorksEdit.value = { id: null, workIds: [] }; // Диалог сам сбросит visible
  enableScroll(); // Восстанавливаем прокрутку
};

// Опции для статуса (копируем из OrderCreateForm для консистентности,
// в идеале это может быть вынесено в store или общий файл констант)
const statusOptions = [
  {value: 1, label: 'Не определён'},
  {value: 2, label: 'На согласовании'},
  {value: 3, label: 'В работе'},
  {value: 4, label: 'Просрочено'},
  {value: 5, label: 'Выполнено в срок'},
  {value: 6, label: 'Выполнено НЕ в срок'},
  {value: 7, label: 'Не согласовано'},
  {value: 8, label: 'На паузе'},
];


/**
 * Обработчик изменения статуса заказа
 * @param orderId - ID заказа
 * @param statusId - ID нового статуса
 */
const handleStatusChange = async (orderId: string, statusId: number) => {
  try {
    console.log(`Статус для заказа ${orderId} изменен на ${statusId}`);

    // Используем существующий метод updateOrder
    await ordersStore.updateOrder(orderId, { status_id: statusId });

    // Показываем уведомление об успехе через PrimeVue Toast
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Статус заказа #${orderId} успешно изменен`,
      life: 3000
    });

  } catch (error) {
    console.error('Ошибка при изменении статуса:', error);
    // Показываем уведомление об ошибке
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Не удалось изменить статус заказа #${orderId}`,
      life: 5000
    });
    // Важно: Откатить локальное изменение в UI, если store не обрабатывает ошибки автоматически
    // Это может потребовать перезапроса данных или более сложной логики отката
    // Для простоты пока оставим так, но в реальном приложении это нужно учесть.
    // Возможно, стоит перезапросить данные, чтобы вернуть старое значение
    await fetchOrders({ skip: currentSkip.value, limit: currentLimit.value, showEnded: showEndedOrders.value });
  }
};
</script>


<template>
  <div :class="mainContainerClass">
    <Toast/>

    <!-- Модальное окно редактирования названия заказа -->
    <OrderNameEditDialog
        v-model:visible="showNameEditDialog"
        :order-id="selectedOrderForNameEdit.id"
        :initial-name="selectedOrderForNameEdit.name"
        @update-name="handleNameUpdated"
        @cancel="handleNameEditCancel"
    />

    <!-- Модальное окно редактирования списка работ -->
    <OrderWorksEditDialog
        v-model:visible="showWorksEditDialog"
        :order-id="selectedOrderForWorksEdit.id"
        :initial-work-ids="selectedOrderForWorksEdit.workIds"
        @update-works="handleWorksUpdated"
        @cancel="handleWorksEditCancel"
    />


    <!-- Модальное окно создания заказа -->
    <transition name="fade">
      <div v-if="showCreateDialog"
           class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
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
                <SelectButton v-model="showEndedOrders" :options="orderVisibilityOptions"
                              @change="toggleEndedOrders" optionLabel="label" optionValue="value"
                              aria-labelledby="orders-visibility-label" class="text-sm"/>
              </span>


              <span class="flex">
                  <Button
                      @click="findOrders"
                      :label="'Поиск'"
                      severity="secondary"
                      :disabled="'true'"
                      class="mr-2"
                  />
                  <Button
                      @click="addNewOrder"
                      :label="'Добавить'"
                      severity="primary"
                  />
                </span>
            </div>
          </th>
        </tr>
        <tr>

          <!-- Номер -->
          <th :class="thClasses" class="cursor-pointer" @click="ordersStore.setSortField('serial')">
            <div class="flex items-center">
              Номер
              <span class="ml-1">
                <i :class="getSortIcon('serial')"></i>
              </span>
            </div>
          </th>


          <th :class="thClasses">Заказчик</th>

          <!-- Приоритет-->
          <th :class="thClasses" class="cursor-pointer" @click="ordersStore.setSortField('priority')">
            <div class="flex items-center">
              Приоритет
              <span class="ml-1">
                <i :class="getSortIcon('priority')"></i>
              </span>
            </div>
          </th>

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
                    { 'font-bold': [1, 2, 3, 4, 8].includes(order.status_id) }
                ]"
                :style="{ color: getStatusColor(order.status_id) }"
                @click="toggleOrderDetails(order.serial)"
            >
              {{ order.serial }}
            </td>


            <td class="px-4 py-2" :class="tdBaseTextClass">
              <div v-if="counterpartyStore.isLoading" class="flex items-center">
                <span>{{ order.customer }}</span>
              </div>
              <Select
                  v-else
                  v-model="order.customer_id"
                  :options="getCustomerOptions"
                  optionValue="value"
                  filter
                  optionLabel="name"
                  :placeholder="order.customer"
                  class="w-full"
                  :autoFilterFocus="true"
                  @change="handleCustomerChange(order.serial, order.customer_id)"
              >
                <!-- Шаблон для отображения выбранного значения -->
                <template #value="slotProps">
                  <div v-if="slotProps.value" class="flex items-center">
                    <div>
                      {{
                        typeof slotProps.value === 'object' && slotProps.value.name
                            ? slotProps.value.name
                            : getCustomerNameById(slotProps.value)
                      }}
                    </div>
                  </div>
                  <span v-else>
                    {{ order.customer }}
                  </span>
                </template>

                <!-- Шаблон для отображения опций -->
                <template #option="slotProps">
                  <div class="flex items-center">
                    <div>{{ slotProps.option.name }}</div>
                  </div>
                </template>
              </Select>
            </td>
            <td class="px-4 py-2" :class="tdBaseTextClass">
              <Select
                  v-model="order.priority"
                  :options="priorityOptions"
                  optionValue="value"
                  optionLabel="label"
                  placeholder="Нет"
                  class="w-full"
                  :clearable="true"
                  @change="handlePriorityChange(order.serial, order.priority)"
              >
                <template #option="slotProps">
                  <div class="flex items-center">
                    <div v-if="slotProps.option.value !== null" class="w-3 h-3 rounded-full mr-2"
                         :class="`priority-indicator priority-${slotProps.option.value}`"></div>
                    <span>{{ slotProps.option.label }}</span>
                  </div>
                </template>
                <template #value="slotProps">
                  <div v-if="slotProps.value" class="flex items-center">
                    <div class="w-3 h-3 rounded-full mr-2"
                         :class="`priority-indicator priority-${slotProps.value}`"></div>
                    <span>{{ priorityOptions.find(opt => opt.value === slotProps.value)?.label }}</span>
                  </div>
                  <span v-else>Нет</span>
                </template>
              </Select>
            </td>

            <!-- В таблице добавим возможность изменить название при клике -->
            <td class="px-4 py-2 cursor-pointer hover:bg-opacity-10 hover:bg-blue-500 transition-colors"
                :class="tdBaseTextClass"
                @click="openNameEditDialog(order.serial, order.name)">
              <div class="flex items-center">
                {{ order.name }}
                <i class="ml-2 text-xs opacity-50"></i>
              </div>
            </td>

            <td class="px-4 py-2 cursor-pointer hover:bg-opacity-10 hover:bg-blue-500 transition-colors"
                :class="tdBaseTextClass"
                @click="openWorksEditDialog(order.serial, order.works)">
              <div class="flex items-center justify-between">
                <div v-if="order.works && order.works.length > 0">
                  <p v-for="work in order.works" :key="work.id" class="text-sm leading-tight"> • {{ work.name }} </p>
                </div>
                <div v-else class="text-xs text-gray-400 italic">
                  Нет работ
                </div>

                <i class="ml-2 text-xs opacity-30 flex-shrink-0"></i>
              </div>
            </td>

            <td class="px-4 py-2" :class="tdBaseTextClass">
              <Select
                  v-model="order.status_id"
                  :options="statusOptions"
                  optionValue="value"
                  optionLabel="label"
                  placeholder="Выберите статус"
                  class="w-full"
                  @change="handleStatusChange(order.serial, order.status_id)"
              >

                <template #value="slotProps">
                   <span v-if="slotProps.value" :style="{ color: getStatusColor(slotProps.value) }">
                     {{ statusOptions.find(opt => opt.value === slotProps.value)?.label || 'Неизвестный статус' }}
                   </span>
                  <span v-else>{{ slotProps.placeholder }}</span>
                </template>

                <template #option="slotProps">
                  <div class="flex items-center">
                      <span :style="{ color: getStatusColor(slotProps.option.value) }">
                        {{ slotProps.option.label }}
                      </span>
                  </div>
                </template>
              </Select>
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

                  <CommentBlock
                      :comments="currentOrderDetail?.comments"
                      :theme="currentTheme"
                  />

                  <div class="flex flex-col gap-4">

                    <!-- Блок с датами -->
                    <DateBlock
                        :order="currentOrderDetail"
                        :theme="currentTheme"
                        :detailBlockClass="detailBlockClass"
                        :detailHeaderClass="detailHeaderClass"
                        :tdBaseTextClass="tdBaseTextClass"
                    />

                    <!-- Блок с финансами -->
                    <FinanceBlock
                        :finance="currentOrderDetail"
                        :theme="currentTheme"
                        :detailBlockClass="detailBlockClass"
                        :detailHeaderClass="detailHeaderClass"
                        :tdBaseTextClass="tdBaseTextClass"
                    />

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

:deep(.p-dialog-header) {
  padding: 1rem;
  border-bottom: 1px solid v-bind('currentTheme === "dark" ? "rgba(75, 85, 99, 1)" : "rgba(229, 231, 235, 1)"');
}

:deep(.p-dialog-content) {
  padding: 0;
}


</style>