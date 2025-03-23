<script setup lang="ts">
import {onUnmounted, ref} from 'vue'
import ImportButton from '../Buttons/ImportButton.vue'; //
import BaseButton from "../Buttons/BaseButton.vue";


// Интерфейс ответа API импорта
interface ImportResponse {
  status: string;
  added?: number;
  updated?: number;
  unchanged?: number;
}

// Интерфейс для пропсов компонента
interface Props {
  url: string;
  endpoint: string;
  buttonText?: string;
  maxHeight?: string;
  importName?: string;
  importButtonText?: string;
}

const props = withDefaults(defineProps<Props>(), {
  buttonText: 'Получить данные',
  maxHeight: '400px',
  importName: '',
  importButtonText: 'Импорт'
});

const tableData = ref<any[]>([])
const tableHeaders = ref<string[]>([])
const connectionError = ref<string>('')
const importStatus = ref<string>('') // Для отображения статуса импорта
const isImporting = ref<boolean>(false) // Флаг, указывающий на процесс импорта
const importButtonState = ref<string>(props.importButtonText)

// **Добавляем ref для хранения результата импорта**
const importResult = ref<ImportResponse | null>(null)

// Для очистки таймера при размонтировании компонента
let buttonResetTimer: ReturnType<typeof setTimeout> | null = null;

onUnmounted(() => {
  if (buttonResetTimer) {
    clearTimeout(buttonResetTimer);
  }
});

async function fetchData(): Promise<void> {
  connectionError.value = '';
  tableData.value = [];
  tableHeaders.value = [];
  importStatus.value = '';

  const timeout = 3000;
  const fetchPromise = fetch(`${props.url}${props.endpoint}`);
  const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Превышено время ожидания запроса')), timeout)
  );

  try {
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    console.log('Статус ответа:', response.status);

    if (!response.ok) {
      connectionError.value = `Ошибка при получении данных: ${response.status} ${response.statusText}`;
      return; // Early return при ошибке
    }

    const data = await response.json();
    console.log('Полученные данные:', data);

    const arrayKey = Object.keys(data).find(key => Array.isArray(data[key]));

    if (!arrayKey || data[arrayKey].length === 0) {
      connectionError.value = 'Некорректный формат данных';
      return; // Early return при ошибке
    }

    tableData.value = data[arrayKey];
    tableHeaders.value = Object.keys(data[arrayKey][0]);

  } catch (error) {
    console.error('Ошибка при получении данных:', error);
    if (error instanceof Error) {
      connectionError.value = error.message;
    } else {
      connectionError.value = 'Неизвестная ошибка';
    }
  }
}

async function importData(): Promise<void> {
  if (!props.importName) {
    connectionError.value = 'Ошибка: не указано имя импорта';
    return;
  }

  // Очищаем предыдущие данные
  await clearData();
  importResult.value = null;

  importStatus.value = 'Выполняется импорт...';
  connectionError.value = '';
  isImporting.value = true;
  importButtonState.value = 'Импортирую...';

  try {
    const response = await fetch(`${props.url}import/${props.importName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json() as ImportResponse;

    if (response.ok) {
      importStatus.value = 'Импорт успешен!';
      importButtonState.value = 'Импорт успешен!';

      // Сохраняем полученные данные в importResult
      importResult.value = data;

    } else {
      const errorText = (data as any).detail || 'Неизвестная ошибка';
      importButtonState.value = `Ошибка!`;
      connectionError.value = `Ошибка импорта: ${errorText}`;
    }
  } catch (error) {
    console.error('Ошибка при импорте:', error);
    importButtonState.value = 'Ошибка!';
    if (error instanceof Error) {
      connectionError.value = `Ошибка импорта: ${error.message}`;
    } else {
      connectionError.value = 'Неизвестная ошибка импорта';
    }
  } finally {
    isImporting.value = false;

    // Возвращаем кнопке исходное состояние через 3 секунды
    if (buttonResetTimer) clearTimeout(buttonResetTimer);

    buttonResetTimer = setTimeout(() => {
      importButtonState.value = props.importButtonText;
      importStatus.value = '';
    }, 3000);
  }
}

async function clearData(): Promise<void> {
  tableData.value = []
  tableHeaders.value = []
  connectionError.value = ""
  importStatus.value = ""
  importResult.value = null;
}


</script>

<template>
  <div class="grid grid-cols-4 gap-2">

    <BaseButton
        :text='buttonText'
        :action="fetchData"
        :style="'Primary'"
    >
    </BaseButton>

    <BaseButton
        :action="clearData"
        :text="'Свернуть'"
        :style="'Secondary'"
    >
    </BaseButton>

    <!-- Кнопка импорта данных -->
    <div v-if="importName">
      <ImportButton
          :importAction="importData"
          :isImporting="isImporting"
          :importStatus="importStatus"
          :importResult="importResult"
          :importButtonText="props.importButtonText"
      />
    </div>

    <div v-if="importName">
      <!-- Добавляем отображение результата импорта -->
      <div v-if="importResult" class="ml-4 text-white bg-gray-700 p-2 rounded">
        <p>Статус:
          <span :class="{'text-green-400 font-bold': importResult.status === 'success'}">
            {{ importResult.status }}
          </span>
        </p>
        <p>Добавлено: {{ importResult.added ?? 0 }}</p>
        <p>Обновлено: {{ importResult.updated ?? 0 }}</p>
        <p>Без изменений: {{ importResult.unchanged ?? 0 }}</p>
      </div>
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