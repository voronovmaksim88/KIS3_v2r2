<!-- src/components/DateBlock.vue -->
<script setup lang="ts">
import { computed } from 'vue';

// Определение типа входных данных для компонента
interface DateData {
  start_moment?: string | null;
  deadline_moment?: string | null;
  end_moment?: string | null;
}

// Определяем пропсы для компонента через деструктуризацию
const props = defineProps<{
  order: DateData | null;
  theme: string;
  detailBlockClass: string;
  detailHeaderClass: string;
  tdBaseTextClass: string;
}>();

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

    // Применяем смещение часового пояса
    const adjustedDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);

    // Извлекаем компоненты даты
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

// Вычисляем количество дней с момента создания
const daysSinceCreation = computed(() => {
  if (!props.order?.start_moment) return null;
  const startDate = new Date(props.order.start_moment);
  const now = new Date();
  const diffTime = now.getTime() - startDate.getTime();
  return Math.floor(diffTime / (1000 * 60 * 60 * 24));
});

// Вычисляем количество дней до дедлайна
const daysUntilDeadline = computed(() => {
  if (!props.order?.deadline_moment) return null;
  const deadlineDate = new Date(props.order.deadline_moment);
  const now = new Date();
  const diffTime = deadlineDate.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
});

// Вычисляем количество дней с момента завершения
const daysSinceCompletion = computed(() => {
  if (!props.order?.end_moment) return null;
  const endDate = new Date(props.order.end_moment);
  const now = new Date();
  const diffTime = now.getTime() - endDate.getTime();
  return Math.floor(diffTime / (1000 * 60 * 60 * 24));
});

// Проверка, просрочен ли дедлайн
const isDeadlineOverdue = computed(() => {
  return daysUntilDeadline.value !== null && daysUntilDeadline.value < 0;
});

// Вспомогательная функция для склонения слова "день"
function getDaysText(days: number): string {
  const lastDigit = days % 10;
  const lastTwoDigits = days % 100;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
    return 'дней';
  }

  if (lastDigit === 1) {
    return 'день';
  }

  if (lastDigit >= 2 && lastDigit <= 4) {
    return 'дня';
  }

  return 'дней';
}
</script>

<template>
  <div :class="detailBlockClass">
    <h4 :class="detailHeaderClass">Даты</h4>

    <table class="w-full border-none table-fixed border-collapse">
      <tbody>
      <tr>
        <td :class="tdBaseTextClass" class="text-left pr-2">
          создан:
        </td>
        <td :class="tdBaseTextClass" class="text-left">
          {{ formatLocalDateTime(props.order?.start_moment, false) || 'не определено' }}
        </td>
        <td v-if="daysSinceCreation !== null" class="text-xs text-gray-500 pl-2 text-left">
          ({{ daysSinceCreation }} {{ getDaysText(daysSinceCreation) }} назад)
        </td>
        <td v-else></td>
      </tr>

      <tr>
        <td :class="tdBaseTextClass" class="text-left pr-2">
          дедлайн:
        </td>
        <td class="text-left">
          {{ formatLocalDateTime(props.order?.deadline_moment, false) || 'не определено' }}
        </td>
        <td
            v-if="daysUntilDeadline !== null"
            class="text-xs pl-2 text-left"
            :class="isDeadlineOverdue ? 'text-red-400' : 'text-gray-500'"
        >
          <template v-if="daysUntilDeadline > 0">
            (через {{ daysUntilDeadline }} {{ getDaysText(daysUntilDeadline) }})
          </template>
          <template v-else-if="daysUntilDeadline === 0">
            (сегодня)
          </template>
          <template v-else>
            (просрочен на {{ Math.abs(daysUntilDeadline) }} {{ getDaysText(Math.abs(daysUntilDeadline)) }})
          </template>
        </td>
        <td v-else></td>
      </tr>

      <tr v-if="props.order?.end_moment">
        <td :class="tdBaseTextClass" class="text-left pr-2">
          завершён:
        </td>
        <td :class="tdBaseTextClass" class="text-left">
          {{ formatLocalDateTime(props.order?.end_moment, false) || 'не определено' }}
        </td>
        <td v-if="daysSinceCompletion !== null" class="text-xs text-gray-500 pl-2 text-left">
          ({{ daysSinceCompletion }} {{ getDaysText(daysSinceCompletion) }} назад)
        </td>
        <td v-else></td>
      </tr>
      </tbody>
    </table>
  </div>
</template>


<style scoped>
table {
  border: none;
  border-collapse: collapse;
}

table tr {
  height: 2rem; /* Выставляет фиксированную высоту строк для лучшего выравнивания */
  border: none;
}

table td {
  padding: 4px 0; /* Вертикальный отступ внутри ячеек для лучшей читаемости */
  border: none;
}

table th {
  border: none;
}
</style>