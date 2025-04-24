<!-- TaskList.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import { typeTask } from '@/types/typeTask';
import TaskNode from './TaskNode.vue';
import { useThemeStore } from "../stores/storeTheme";

interface Props {
  tasks: typeTask[];
  statusMap?: Record<number, string>;
  paymentStatusMap?: Record<number, string>;
}

// Получаем текущую тему из хранилища
const themeStore = useThemeStore();
const currentTheme = computed(() => themeStore.theme);

const props = withDefaults(defineProps<Props>(), {
  statusMap: () => ({
    1: 'Не начата',
    2: 'В работе',
    3: 'На паузе',
    4: 'Завершена',
    5: 'Отменена'
  }),
  paymentStatusMap: () => ({
    1: 'Нет оплаты',
    2: 'Возможна',
    3: 'Начислена',
    4: 'Оплачена'
  })
});

// Вычисляем корневые задачи (у которых root_task_id = null или они сами являются корневыми)
const rootTasks = computed(() => {
  return props.tasks.filter(task =>
      task.root_task_id === null && task.parent_task_id === null
  );
});
</script>

<template>
  <div class="tasks-container rounded-md p-2 border "
       :class="[
         currentTheme === 'dark'
           ? 'bg-gray-800 border-gray-600 shadow-md shadow-gray-900/20'
           : 'bg-white border-gray-300 shadow-sm shadow-gray-200/50'
       ]">
    <h4 class="font-semibold mb-2 transition-colors duration-300"
        :class="[
          currentTheme === 'dark'
            ? 'text-white'
            : 'text-gray-800'
        ]">
      Задачи
    </h4>

    <div v-if="!tasks || tasks.length === 0"
         class="empty-state py-4 text-center rounded-md transition-colors duration-300"
         :class="[
           currentTheme === 'dark'
             ? 'text-gray-400 bg-gray-700/30'
             : 'text-gray-500 bg-gray-50'
         ]">
      <i class="pi pi-list text-2xl mb-2 block opacity-50"></i>
      <span>Нет задач</span>
    </div>

    <div v-else class="tasks-list space-y-1">
      <!-- Отображаем только корневые задачи (задачи без родителей или с root_task_id = null) -->
      <div v-for="task in rootTasks" :key="task.id"
           class="task-item transition-all duration-300"
           :class="[
             currentTheme === 'dark'
               ? 'hover:bg-gray-700/30'
               : 'hover:bg-gray-50'
           ]">
        <TaskNode
            :task="task"
            :all-tasks="tasks"
            :status-map="statusMap"
            :payment-status-map="paymentStatusMap"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.tasks-container {
  /* Базовые стили для контейнера задач */
  position: relative;
  overflow: hidden;
  max-height: 100%;
  width: 100%;
}

.empty-state {
  /* Стили для состояния "Нет задач" */
  margin: 1rem 0;
  padding: 1.5rem;
  border-radius: 0.375rem;
  transition: all 0.3s ease;
}

.task-item {
  /* Стили для каждого элемента задачи */
  position: relative;
  border-radius: 0.375rem;
  padding: 0.25rem;
  transition: all 0.2s ease;
}

/* Медиа-запросы для адаптивности */
@media (max-width: 640px) {
  .tasks-container {
    padding: 0.75rem;
  }

  .empty-state {
    padding: 1rem;
  }
}
</style>