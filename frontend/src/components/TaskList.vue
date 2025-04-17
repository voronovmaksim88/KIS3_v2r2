<!-- TaskList.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import { typeTask } from '@/types/typeTask';
import TaskNode from './TaskNode.vue';

interface Props {
  tasks: typeTask[];
  statusMap?: Record<number, string>;
  paymentStatusMap?: Record<number, string>;
}

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
  <div class="border rounded-md p-3 bg-gray-800">
    <h4 class="font-semibold text-white mb-2">Задачи</h4>
    <div v-if="!tasks || tasks.length === 0" class="text-gray-400">
      Нет задач
    </div>
    <div v-else class="space-y-2">
      <!-- Отображаем только корневые задачи (задачи без родителей или с root_task_id = null) -->
      <div v-for="task in rootTasks" :key="task.id" class="mt-2">
        <TaskNode :task="task" :all-tasks="tasks" :status-map="statusMap" :payment-status-map="paymentStatusMap" />
      </div>
    </div>
  </div>
</template>