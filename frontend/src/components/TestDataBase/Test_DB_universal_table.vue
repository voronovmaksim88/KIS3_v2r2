<script setup>
import {computed, onUnmounted, ref} from 'vue'

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
  },
  // Новое свойство для определения, что импортировать
  importName: {
    type: String,
    default: ''
  },
  // Текст на кнопке импорта
  importButtonText: {
    type: String,
    default: 'Импорт'
  }
});

const tableData = ref([])
const tableHeaders = ref([])
const connectionError = ref('')
const importStatus = ref('') // Для отображения статуса импорта
const isImporting = ref(false) // Флаг, указывающий на процесс импорта
const importButtonState = ref(props.importButtonText)
    //const importButtonClass = ref('btn-accent')

// Для очистки таймера при размонтировании компонента
let buttonResetTimer = null;

onUnmounted(() => {
  if (buttonResetTimer) {
    clearTimeout(buttonResetTimer);
  }
});

async function fetchData() {
  connectionError.value = '';
  tableData.value = [];
  tableHeaders.value = [];
  importStatus.value = '';

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

async function importData() {

  if (!props.importName) {
    connectionError.value = 'Ошибка: не указано имя импорта';
    return;
  }

  clearData()

  importStatus.value = 'Выполняется импорт...';
  connectionError.value = '';
  isImporting.value = true;
  importButtonState.value = 'Импортирую...';
  // Убираем эту строку, класс будет вычисляться автоматически
  // importButtonClass.value = 'btn-loading';

  try {
    const response = await fetch(`${props.url}import/${props.importName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      // Выведем подробную информацию о полученных данных
      console.log('Данные успешного ответа:', data);
      console.log('Тип data.status:', typeof data.status);
      console.log('Значение data.status:', data.status);

      // Упростим проверку - при любом успешном ответе считаем импорт успешным
      importStatus.value = 'Импорт успешен!';
      importButtonState.value = 'Импорт успешен!';

    } else {
      // Ошибка импорта
      const errorText = data.detail || 'Неизвестная ошибка';
      importButtonState.value = `Ошибка!`;
      // Убираем эту строку, класс будет вычисляться автоматически
      // importButtonClass.value = 'btn-error';
      connectionError.value = `Ошибка импорта: ${errorText}`;
    }
  } catch (error) {
    console.error('Ошибка при импорте:', error);
    importButtonState.value = 'Ошибка!';
    // Убираем эту строку, класс будет вычисляться автоматически
    // importButtonClass.value = 'btn-error';
    connectionError.value = `Ошибка импорта: ${error.message}`;
  } finally {
    isImporting.value = false;

    // Возвращаем кнопке исходное состояние через 3 секунды
    if (buttonResetTimer) clearTimeout(buttonResetTimer);

    buttonResetTimer = setTimeout(() => {
      importButtonState.value = props.importButtonText;
      importStatus.value = ''; // Сбрасываем статус вместо класса
    }, 3000);
  }
}

function clearData() {
  tableData.value = []
  tableHeaders.value = []
  connectionError.value = ""
  importStatus.value = ""
}

// Вычисляемое свойство для Tailwind классов
const tailwindButtonClasses = computed(() => {
  // Добавьте отладочное сообщение
  console.log('Текущий статус импорта:', importStatus.value);
  console.log('Условие для зеленой кнопки:', importStatus.value === 'Импорт успешен!');

  if (isImporting.value) {
    return 'bg-yellow-400 text-yellow-900 hover:bg-yellow-500 focus:ring-yellow-500 cursor-wait';
  }
  if (importStatus.value === 'Импорт успешен!') {
    return 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-700';
  }
  if (connectionError.value.includes('Ошибка импорта')) {
    return 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-700';
  }
  return 'bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-100';
});
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <div class="col-span-2">
      <button class="btn btn-p w-full" @click="fetchData">{{ buttonText }}</button>
    </div>



    <div>
      <button class="btn btn-s w-full" @click="clearData">Свернуть</button>
    </div>

    <!-- Кнопка импорта с Tailwind классами -->
    <div v-if="importName">
      <button
          class="w-full py-2 px-4 rounded font-bold transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-opacity-50"
          :class="tailwindButtonClasses"
          @click="importData"
          :disabled="isImporting"
      >
        {{ importButtonState }}
      </button>
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