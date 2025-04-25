<!-- TaskDetailView.vue -->
<script setup lang="ts">
import {computed} from 'vue';
import {typeTask} from "@/types/typeTask.ts";
import {formatFIO} from "@/utils/formatFIO.ts";
import BaseModal from '@/components/BaseModal.vue';
import 'primeicons/primeicons.css';
import {useThemeStore} from "@/stores/storeTheme.ts"; // Импортируем хранилище темы

interface Props {
  task: typeTask;
  statusMap: Record<number, string>;
  paymentStatusMap: Record<number, string>;
  onClose?: () => void;
}

const props = defineProps<Props>();

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

// Определяем, просрочена ли задача
const isOverdue = computed(() => {
  if (!props.task.deadline_moment) return false;
  if (props.task.status_id === 4) return false; // Если задача завершена, она не просрочена

  const deadline = new Date(props.task.deadline_moment);
  const now = new Date();
  return deadline < now;
});

// Получаем текущую тему из хранилища
const themeStore = useThemeStore();
const currentTheme = computed(() => themeStore.theme);

// Вычисляемые свойства для цветов в зависимости от темы
const bgContentClass = computed(() => currentTheme.value === 'dark' ? 'bg-gray-700' : 'bg-gray-50');
const textSecondaryClass = computed(() => currentTheme.value === 'dark' ? 'text-gray-300' : 'text-gray-600');
const borderClass = computed(() => currentTheme.value === 'dark' ? 'border-gray-700' : 'border-gray-200');
</script>

<template>
  <BaseModal :name="task.name" :onClose="onClose">
    <!-- Основные данные в формате название-значение -->
    <div class="grid grid-cols-1 gap-4 mb-6">

      <!-- Статус -->
      <div class="grid grid-cols-4 gap-4">
        <div :class="textSecondaryClass" class="transition-colors duration-300 font-medium">Статус:</div>
        <div class="col-span-3">
          <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
            <div class="flex items-center">
              <div :class="[statusColor, 'w-3 h-3 rounded-full mr-2']"></div>
              <span>{{ statusMap[task.status_id] || 'Неизвестный статус' }}</span>
              <span v-if="isOverdue" class="ml-3 flex items-center text-red-400">
            <i class="pi pi-exclamation-circle mr-1"></i>
            <span>Просрочена</span>
          </span>
            </div>
          </div>
        </div>
      </div>


      <!-- Описание -->
      <div class="grid grid-cols-4 gap-4">
        <div :class="textSecondaryClass" class="transition-colors duration-300 font-medium">Описание:</div>
        <div class="col-span-3">
          <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
            <p v-if="task.description">{{ task.description }}</p>
            <p v-else :class="currentTheme === 'dark' ? 'text-gray-400 italic' : 'text-gray-500 italic'">Описание
              отсутствует</p>
          </div>
        </div>
      </div>

      <!-- Исполнитель -->
      <div class="grid grid-cols-4 gap-4">
        <div :class="textSecondaryClass" class="transition-colors duration-300 font-medium">Исполнитель:</div>
        <div class="col-span-3">
          <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
            <p v-if="task.executor">{{ formatFIO(task.executor) }}</p>
            <p v-else :class="currentTheme === 'dark' ? 'text-gray-400 italic' : 'text-gray-500 italic'">Не назначен</p>
          </div>
        </div>
      </div>

      <!-- Временные показатели -->
      <div class="grid grid-cols-4 gap-4">
        <div :class="textSecondaryClass" class="transition-colors duration-300 font-medium">Время:</div>
        <div class="col-span-3">
          <div :class="[bgContentClass, 'rounded-md p-4 transition-colors duration-300 border', borderClass]">
            <div class="grid grid-cols-1 gap-2">
              <div class="grid grid-cols-2 gap-2">
                <div :class="textSecondaryClass" class="transition-colors duration-300">Создана:</div>
                <div>{{ formatDateTime(task.creation_moment) }}</div>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div :class="textSecondaryClass" class="transition-colors duration-300">Начата:</div>
                <div>{{ formatDateTime(task.start_moment) }}</div>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div :class="textSecondaryClass" class="transition-colors duration-300">Дедлайн:</div>
                <div :class="{ 'text-red-400': isOverdue }">
                  {{ formatDateTime(task.deadline_moment) }}
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div :class="textSecondaryClass" class="transition-colors duration-300">Завершена:</div>
                <div>{{ formatDateTime(task.end_moment) }}</div>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div :class="textSecondaryClass" class="transition-colors duration-300">План. длительность:</div>
                <div>{{ formatDuration(task.planned_duration) }}</div>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div :class="textSecondaryClass" class="transition-colors duration-300">Факт. длительность:</div>
                <div>{{ formatDuration(task.actual_duration) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </BaseModal>
</template>