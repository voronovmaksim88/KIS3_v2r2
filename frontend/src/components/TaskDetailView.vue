<!-- TaskDetailView.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import { typeTask } from "@/types/typeTask.ts";
import { formatFIO } from "@/utils/formatFIO.ts";

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

// Для форматирования длительности
const formatDuration = (durationString: string | null): string => {
  if (!durationString) return 'Не указано';

  // Предполагаем, что длительность в формате ISO или в часах
  // Можно адаптировать под ваш формат данных
  try {
    const hours = parseFloat(durationString);
    return `${hours} ч.`;
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
      return 'bg-yellow-500';
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
  <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden max-w-4xl w-full mx-auto">
    <!-- Шапка с названием и кнопкой закрытия -->
    <div class="bg-gray-700 px-6 py-4 flex justify-between items-center">
      <h2 class="text-xl font-semibold text-white truncate">{{ task.name }}</h2>
      <button
          v-if="onClose"
          @click="onClose"
          class="text-gray-400 hover:text-white"
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
          <span class="text-white">{{ statusMap[task.status_id] || 'Неизвестный статус' }}</span>
        </div>

<!--          пока сомневаюсь что надо стоимость задач и отслеживание оплат вести в кис3-->
<!--        <div class="flex items-center">-->
<!--          <div :class="[paymentStatusColor, 'w-3 h-3 rounded-full mr-2']"></div>-->
<!--          <span class="text-white">{{ paymentStatusMap[task.payment_status_id] || 'Статус оплаты не указан' }}</span>-->
<!--        </div>-->

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
        <h3 class="text-lg font-medium text-gray-300 mb-2">Описание</h3>
        <div class="bg-gray-700 rounded-md p-4 text-white">
          <p v-if="task.description">{{ task.description }}</p>
          <p v-else class="text-gray-400 italic">Описание отсутствует</p>
        </div>
      </div>

      <!-- Исполнитель и время -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Левая колонка: исполнитель и цена -->
        <div>
          <h3 class="text-lg font-medium text-gray-300 mb-2">Исполнитель</h3>
          <div class="bg-gray-700 rounded-md p-4 text-white">
            <p v-if="task.executor">{{ formatFIO(task.executor) }}</p>
            <p v-else class="text-gray-400 italic">Не назначен</p>
          </div>

<!--          пока сомневаюсь что надо стоимость задач и отслеживание оплат вести в кис3-->
<!--          <h3 class="text-lg font-medium text-gray-300 mt-4 mb-2">Стоимость</h3>-->
<!--          <div class="bg-gray-700 rounded-md p-4 text-white">-->
<!--            <p>{{ formattedPrice }}</p>-->
<!--          </div>-->
        </div>

        <!-- Правая колонка: временные показатели -->
        <div>
          <h3 class="text-lg font-medium text-gray-300 mb-2">Временные показатели</h3>
          <div class="bg-gray-700 rounded-md p-4 text-white">
            <div class="grid grid-cols-2 gap-2">
              <div class="text-gray-400">Создана:</div>
              <div>{{ formatDateTime(task.creation_moment) }}</div>

              <div class="text-gray-400">Начата:</div>
              <div>{{ formatDateTime(task.start_moment) }}</div>

              <div class="text-gray-400">Дедлайн:</div>
              <div :class="{ 'text-red-400': isOverdue }">
                {{ formatDateTime(task.deadline_moment) }}
              </div>

              <div class="text-gray-400">Завершена:</div>
              <div>{{ formatDateTime(task.end_moment) }}</div>

              <div class="text-gray-400">План. длительность:</div>
              <div>{{ formatDuration(task.planned_duration) }}</div>

              <div class="text-gray-400">Факт. длительность:</div>
              <div>{{ formatDuration(task.actual_duration) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-gray-700 {
  background-color: rgba(55, 65, 81, 1);
}

.bg-gray-800 {
  background-color: rgba(31, 41, 55, 1);
}

/* Добавим плавные переходы для эффектов наведения */
button {
  transition: all 0.2s ease;
}
</style>