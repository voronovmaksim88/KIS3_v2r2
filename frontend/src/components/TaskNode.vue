<!-- TaskNode.vue -->

<script setup lang="ts">
import { computed, ref } from 'vue';
import { typeTask} from "@/types/typeTask.ts";
// Импорт стилей PrimeIcons
import 'primeicons/primeicons.css';
import {formatFIO} from "@/utils/formatFIO.ts";

interface Props {
  task: typeTask;
  allTasks: typeTask[];
  statusMap: Record<number, string>;
}

const props = defineProps<Props>();
const isExpanded = ref(false);

// Находим все прямые дочерние задачи для текущей задачи
const childTasks = computed(() => {
  return props.allTasks.filter(t => t.parent_task_id === props.task.id);
});

// Проверяем, есть ли у задачи дочерние элементы
const hasChildren = computed(() => childTasks.value.length > 0);

// Переключение состояния развернутости только если есть дочерние задачи
const toggleExpand = () => {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value;
  }
};

function getStatusBackgroundClass(statusId:number) {
  // Возвращаем CSS класс в зависимости от статуса задачи
  switch (statusId) {
    case 1: // "Не начата"
      return 'bg-opacity-30 bg-gray-500'
    case 2: // "В работе"
      return 'bg-opacity-30 bg-green-500'
    case 3: // "На паузе"
      return 'bg-opacity-30 bg-white'
    case 4: // "Завершена"
      return 'bg-opacity-30 bg-blue-500'
    case 5: // "Отменена"
      return 'bg-opacity-30 bg-red-500'
    default:
      return 'bg-opacity-30 bg-gray-900' // По умолчанию серый, если статус неизвестен
  }
}
</script>

<template>
  <div class="task-node border rounded-md p-2"
       :class="[
         getStatusBackgroundClass(task.status_id),
         {'hover:bg-opacity-50': !isExpanded},
       ]">
    <!-- Заголовок задачи (кликабельный для разворачивания, только если есть дочерние задачи) -->
    <div @click="toggleExpand"
         class="flex items-center justify-between px-2 py-1"
         :class="{'cursor-pointer': hasChildren}">
      <!-- Левая часть - стрелка и название задачи -->
      <div class="flex items-center">
        <!-- Стрелка для разворачивания/сворачивания (если есть дочерние задачи) -->
        <span v-if="hasChildren" class="mr-2 text-gray-300">
          <i :class="isExpanded ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"></i>
        </span>
        <span v-else class="mr-2 w-4"></span> <!-- Пустое пространство для выравнивания -->

        <!-- Название задачи -->
        <div class="font-medium text-white">{{ task.name }}</div>
      </div>

      <!-- Правая часть - исполнитель -->
      <div v-if="task.executor" class="text-xs text-gray-300">
        {{ formatFIO(task.executor) }}
      </div>
    </div>

    <!-- Раскрывающаяся информация о задаче - отображаем только если есть дочерние задачи -->
    <div v-if="isExpanded && hasChildren" class="pl-4 mt-2">
      <!-- Подзадачи -->
      <div class="mt-2 space-y-2 border-l-2 border-gray-100 pl-3">
        <div v-for="childTask in childTasks" :key="childTask.id" class="mt-1">
          <TaskNode
              :task="childTask"
              :all-tasks="allTasks"
              :status-map="statusMap"
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