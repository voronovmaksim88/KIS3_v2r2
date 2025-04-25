<!-- TaskDetailView.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import { typeTask } from "@/types/typeTask.ts";
import { formatFIO } from "@/utils/formatFIO.ts";
import { useThemeStore } from "@/stores/storeTheme.ts"; // Импортируем хранилище темы

interface Props {
  task: typeTask;
  statusMap: Record<number, string>;
  paymentStatusMap: Record<number, string>;
  onClose?: () => void;
}

const props = defineProps<Props>();

// Получаем текущую тему из хранилища
const themeStore = useThemeStore();
const currentTheme = computed(() => themeStore.theme);

// Вычисляемые свойства для цветов в зависимости от темы
const bgMainClass = computed(() => currentTheme.value === 'dark' ? 'bg-gray-800' : 'bg-white');
const bgHeaderClass = computed(() => currentTheme.value === 'dark' ? 'bg-gray-700' : 'bg-gray-100');
const bgContentClass = computed(() => currentTheme.value === 'dark' ? 'bg-gray-700' : 'bg-gray-50');
const textMainClass = computed(() => currentTheme.value === 'dark' ? 'text-white' : 'text-gray-800');
const textSecondaryClass = computed(() => currentTheme.value === 'dark' ? 'text-gray-300' : 'text-gray-600');
const borderClass = computed(() => currentTheme.value === 'dark' ? 'border-gray-700' : 'border-gray-200');

// Для форматирования дат
const formatDateTime = (dateString: string | null): string => {
  if (!dateString) return 'Не указано';

  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// Для форматирования длительности в ISO 8601 формате
const formatDuration = (durationString: string | null): string => {
  if (!durationString) return 'Не указано';

  // Проверяем, что строка в формате ISO 8601 для длительности
  if (durationString.startsWith('P')) {
    try {
      // Регулярные выражения для извлечения компонентов длительности
      const dayMatch = durationString.match(/(\d+)D/);
      const hourMatch = durationString.match(/(\d+)H/);
      const minuteMatch = durationString.match(/(\d+)M/);

      const days = dayMatch ? parseInt(dayMatch[1]) : 0;
      const hours = hourMatch ? parseInt(hourMatch[1]) : 0;
      const minutes = minuteMatch ? parseInt(minuteMatch[1]) : 0;

      // Создаем понятную текстовую репрезентацию
      let result = '';

      if (days > 0) {
        result += `${days} д. `;
      }

      if (hours > 0 || days > 0) {
        result += `${hours} ч. `;
      }

      if (minutes > 0 || hours > 0 || days > 0) {
        result += `${minutes} м. `;
      }

      if (result === '') {
        return '0 м.';
      }

      return result.trim();
    } catch (error) {
      console.error('Ошибка при парсинге длительности:', error);
      return 'Ошибка формата';
    }
  }

  // Пытаемся обработать как число часов для обратной совместимости
  try {
    const hours = parseFloat(durationString);
    if (!isNaN(hours)) {
      return `${hours} ч.`;
    }
    return durationString;
  } catch {
    return durationString;
  }
};


// Вычисляемое свойство для определения цвета индикатора статуса
const statusColor = computed(() => {
  switch (props.task.status_id) {
    case 1: // "Не начата"
      return 'bg-gray-500';
    case 2: // "В работе"
      return 'bg-green-500';
    case 3: // "На паузе"
      return 'bg-purple-500';
    case 4: // "Завершена"
      return 'bg-blue-500';
    case 5: // "Отменена"
      return 'bg-red-500';
    default:
      return 'bg-gray-400';
  }
});

// Вычисляемое свойство для определения цвета индикатора статуса оплаты
// const paymentStatusColor = computed(() => {
//   switch (props.task.payment_status_id) {
//     case 1: // "Не оплачено"
//       return 'bg-red-500';
//     case 2: // "Частично оплачено"
//       return 'bg-yellow-500';
//     case 3: // "Полностью оплачено"
//       return 'bg-green-500';
//     default:
//       return 'bg-gray-400';
//   }
// });

// Вычисляемое свойство для отображения цены
// const formattedPrice = computed(() => {
//   if (props.task.price === null) return 'Не указана';
//   return `${props.task.price.toLocaleString('ru-RU')} ₽`;
// });

// Определяем, просрочена ли задача
const isOverdue = computed(() => {
  if (!props.task.deadline_moment) return false;
  if (props.task.status_id === 4) return false; // Если задача завершена, она не просрочена

  const deadline = new Date(props.task.deadline_moment);
  const now = new Date();
  return deadline < now;
});
</script>

<template>
  <div :class="[bgMainClass, 'rounded-lg shadow-lg overflow-hidden max-w-4xl w-full mx-auto border transition-colors duration-300', borderClass]">
    <!-- Шапка с названием и кнопкой закрытия -->
    <div :class="[bgHeaderClass, 'px-6 py-4 flex justify-between items-center transition-colors duration-300']">
      <h2 :class="[textMainClass, 'text-xl font-semibold truncate transition-colors duration-300']">{{ task.name }}</h2>
      <button
          v-if="onClose"
          @click="onClose"
          :class="[currentTheme === 'dark' ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-800']"
          class="transition-colors duration-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="p-6">
      <!-- Статусы -->
      <div class="flex flex-wrap gap-4 mb-6">
        <div class="flex items-center">
          <div :class="[statusColor, 'w-3 h-3 rounded-full mr-2']"></div>
          <span :class="textMainClass">{{ statusMap[task.status_id] || 'Неизвестный статус' }}</span>
        </div>

        <div v-if="isOverdue" class="flex items-center text-red-400">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>Просрочена</span>
        </div>
      </div>

      <!-- Описание -->
      <div class="mb-6">
        <h3 :class="[textSecondaryClass, 'text-lg font-medium mb-2 transition-colors duration-300']">Описание</h3>
        <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
          <p v-if="task.description" :class="textMainClass">{{ task.description }}</p>
          <p v-else :class="currentTheme === 'dark' ? 'text-gray-400 italic' : 'text-gray-500 italic'">Описание отсутствует</p>
        </div>
      </div>

      <!-- Исполнитель и время -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Левая колонка: исполнитель и цена -->
        <div>
          <h3 :class="[textSecondaryClass, 'text-lg font-medium mb-2 transition-colors duration-300']">Исполнитель</h3>
          <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
            <p v-if="task.executor" :class="textMainClass">{{ formatFIO(task.executor) }}</p>
            <p v-else :class="currentTheme === 'dark' ? 'text-gray-400 italic' : 'text-gray-500 italic'">Не назначен</p>
          </div>
        </div>

        <!-- Правая колонка: временные показатели -->
        <div>
          <h3 :class="[textSecondaryClass, 'text-lg font-medium mb-2 transition-colors duration-300']">Временные показатели</h3>
          <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
            <div class="grid grid-cols-2 gap-2">
              <div :class="textSecondaryClass" class="transition-colors duration-300">Создана:</div>
              <div :class="textMainClass">{{ formatDateTime(task.creation_moment) }}</div>

              <div :class="textSecondaryClass" class="transition-colors duration-300">Начата:</div>
              <div :class="textMainClass">{{ formatDateTime(task.start_moment) }}</div>

              <div :class="textSecondaryClass" class="transition-colors duration-300">Дедлайн:</div>
              <div :class="{ 'text-red-400': isOverdue, [textMainClass]: !isOverdue }">
                {{ formatDateTime(task.deadline_moment) }}
              </div>

              <div :class="textSecondaryClass" class="transition-colors duration-300">Завершена:</div>
              <div :class="textMainClass">{{ formatDateTime(task.end_moment) }}</div>

              <div :class="textSecondaryClass" class="transition-colors duration-300">План. длительность:</div>
              <div :class="textMainClass">{{ formatDuration(task.planned_duration) }}</div>

              <div :class="textSecondaryClass" class="transition-colors duration-300">Факт. длительность:</div>
              <div :class="textMainClass">{{ formatDuration(task.actual_duration) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Добавим плавные переходы для эффектов наведения */
button {
  transition: all 0.2s ease;
}
</style>