<!-- TaskNode.vue -->

<script setup lang="ts">
import { computed, ref } from 'vue';
import { typeTask} from "@/types/typeTask.ts";
// Импорт стилей PrimeIcons
import 'primeicons/primeicons.css';


interface Props {
  task: typeTask;
  allTasks: typeTask[];
  statusMap: Record<number, string>;
  paymentStatusMap: Record<number, string>;
}

const props = defineProps<Props>();
const isExpanded = ref(false);

// Находим все прямые дочерние задачи для текущей задачи
const childTasks = computed(() => {
  return props.allTasks.filter(t => t.parent_task_id === props.task.id);
});

// Проверяем, есть ли у задачи дочерние элементы
const hasChildren = computed(() => childTasks.value.length > 0);

// Переключение состояния развернутости
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};

// Получение цвета для статуса оплаты
// const getPaymentStatusSeverity = (statusId: number): string => {
//   const map: Record<number, string> = {
//     1: 'secondary', // Нет оплаты
//     2: 'info',      // Возможна
//     3: 'warning',   // Начислена
//     4: 'success'    // Оплачена
//   };
//   return map[statusId] || 'secondary';
// };

// // Форматирование длительности из строки ISO 8601 в читаемый формат
// const formatDuration = (duration: string): string => {
//   try {
//     // Предполагается, что duration в формате ISO 8601 (например, "PT2H30M")
//     const matches = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
//     if (!matches) return duration;
//
//     const hours = matches[1] ? parseInt(matches[1]) : 0;
//     const minutes = matches[2] ? parseInt(matches[2]) : 0;
//     const seconds = matches[3] ? parseInt(matches[3]) : 0;
//
//     let result = '';
//     if (hours) result += `${hours}ч `;
//     if (minutes) result += `${minutes}м `;
//     if (seconds && !hours) result += `${seconds}с`;
//
//     return result.trim();
//   } catch (e) {
//     return duration;
//   }
// };
//
// // Форматирование даты в читаемый формат
// const formatDate = (dateString: string): string => {
//   try {
//     const date = new Date(dateString);
//     return new Intl.DateTimeFormat('ru-RU', {
//       day: '2-digit',
//       month: '2-digit',
//       year: 'numeric',
//       hour: '2-digit',
//       minute: '2-digit'
//     }).format(date);
//   } catch (e) {
//     return dateString;
//   }
// };
</script>


<template>
  <div class="task-node border rounded-md p-2" :class="{'bg-gray-700': isExpanded, 'hover:bg-gray-700': !isExpanded}">
    <!-- Заголовок задачи (кликабельный для разворачивания) -->
    <div @click="toggleExpand" class="flex items-center justify-between cursor-pointer px-2 py-1">
      <div class="flex items-center">
        <span v-if="hasChildren" class="mr-2 text-gray-300">
          <i :class="isExpanded ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"></i>
        </span>
        <div>
          <div class="font-medium text-white">{{ task.name }}</div>
          <div class="flex text-xs text-gray-400 space-x-2">
            <span v-if="task.executor_id">| Исполнитель: {{ task.executor_id }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Раскрывающаяся информация о задаче -->
    <div v-if="isExpanded" class="pl-4 mt-2">
      <div v-if="task.description" class="text-sm text-gray-300 mb-2 p-2 bg-gray-800 rounded">
        {{ task.description }}
      </div>

      <!-- Подзадачи (если есть) -->
      <div v-if="childTasks.length > 0" class="mt-2 space-y-2 border-l-2 border-gray-600 pl-3">
        <div v-for="childTask in childTasks" :key="childTask.id" class="mt-1">
          <TaskNode
              :task="childTask"
              :all-tasks="allTasks"
              :status-map="statusMap"
              :payment-status-map="paymentStatusMap"
          />
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.task-node {
  transition: all 0.2s ease;
}
</style>