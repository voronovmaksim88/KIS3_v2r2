<script setup lang="ts">
import { computed } from 'vue';
import { formatFIO } from "@/utils/formatFIO.ts";

// Определение типа для комментария
interface Comment {
  moment_of_creation: string;
  person: string;
  text: string;
}

// Входные свойства компонента
const props = defineProps({
  comments: {
    type: Array as () => Comment[],
    default: () => []
  },
  theme: {
    type: String,
    default: 'light'
  }
});

// Вычисляемые стили в зависимости от темы
const detailBlockClass = computed(() => {
  const base = 'border rounded-md p-3 h-full transition-colors duration-300 ease-in-out';
  return props.theme === 'dark'
      ? `${base} bg-gray-800 border-gray-600`
      : `${base} bg-white border-gray-200 shadow-sm`;
});

const detailHeaderClass = computed(() => {
  const base = 'font-semibold mb-2';
  return props.theme === 'dark'
      ? `${base} text-white`
      : `${base} text-gray-800`;
});

const detailSubtleTextClass = computed(() => {
  return props.theme === 'dark' ? 'text-gray-400' : 'text-gray-500';
});

const commentItemClass = computed(() => {
  const base = 'border rounded-md p-2 mb-2 transition-colors duration-300 ease-in-out';
  return props.theme === 'dark'
      ? `${base} border-gray-700 bg-gray-850`
      : `${base} border-gray-300 bg-gray-100`;
});

const tdBaseTextClass = computed(() => {
  return props.theme === 'dark' ? 'text-gray-100' : 'text-gray-800';
});

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
</script>

<template>
  <div :class="detailBlockClass">
    <h4 :class="detailHeaderClass">Комментарии</h4>
    <div
        v-if="!comments || comments.length === 0"
        :class="detailSubtleTextClass"
    >
      Нет комментариев
    </div>
    <div v-else class="space-y-2">
      <div
          v-for="(comment, index) in comments"
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
</template>