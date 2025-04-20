<!-- TaskNode.vue -->

<script setup lang="ts">
import { computed, ref } from 'vue';
import { typeTask} from "@/types/typeTask.ts";
// Импорт стилей PrimeIcons
import 'primeicons/primeicons.css';
import {formatFIO} from "@/utils/formatFIO.ts";
import TaskDetailView from './TaskDetailView.vue'; // Импортируем компонент с детальной информацией

interface Props {
  task: typeTask;
  allTasks: typeTask[];
  statusMap: Record<number, string>;
  paymentStatusMap: Record<number, string>; // Добавляем карту статусов оплаты
}

const props = defineProps<Props>();
const isExpanded = ref(false);
const showDetails = ref(false); // Состояние для отображения детальной информации

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

// Открытие/закрытие детальной информации о задаче
const toggleTaskDetails = () => {
  showDetails.value = !showDetails.value;
};

// Закрытие детальной информации о задаче
const closeTaskDetails = () => {
  showDetails.value = false;
};

function getStatusBackgroundClass(statusId:number) {
  // Возвращаем CSS класс в зависимости от статуса задачи
  switch (statusId) {
    case 1: // "Не начата"
      return 'bg-opacity-30 bg-gray-500'
    case 2: // "В работе"
      return 'bg-opacity-30 bg-green-500'
    case 3: // "На паузе"
      return 'bg-opacity-30 bg-yellow-500'
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
  <div class="task-node border rounded-md p-1"
       :class="[
         getStatusBackgroundClass(task.status_id),
         {'hover:bg-opacity-50': !isExpanded},
       ]">
    <!-- Заголовок задачи (кликабельный для разворачивания, только если есть дочерние задачи) -->
    <div
        class="flex items-center justify-between pr-2 py-1"
        @click="toggleTaskDetails"
    >
      <!-- Левая часть - стрелка и название задачи -->
      <div class="flex items-center">
        <!-- Стрелка для разворачивания/сворачивания (если есть дочерние задачи) -->
        <span v-if="hasChildren"
              class="mr-1 text-gray-300 border rounded-md px-2 py-1"
              @click.stop="toggleExpand"
        >
          <i :class="isExpanded ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"></i>
        </span>
        <span v-else class="mr-2 w-4"></span> <!-- Пустое пространство для выравнивания -->

        <!-- Название задачи (кликабельное для открытия деталей) -->
        <div
            class="font-medium text-white cursor-pointer"
        >
          {{ task.name }}
        </div>
      </div>

      <!-- Правая часть - исполнитель -->
      <div v-if="task.executor" class="text-xs text-gray-300">
        {{ formatFIO(task.executor) }}
      </div>
    </div>

    <!-- Модальное окно с детальной информацией о задаче -->
    <transition name="fade">
      <div v-if="showDetails" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeTaskDetails">
        <div class="max-w-4xl w-full">
          <TaskDetailView
              :task="task"
              :statusMap="statusMap"
              :paymentStatusMap="paymentStatusMap"
              :onClose="closeTaskDetails"
          />
        </div>
      </div>
    </transition>

    <!-- Используем компонент transition для анимации раскрытия/сворачивания -->
    <transition name="expand">
      <div v-if="isExpanded && hasChildren" class="content-wrapper pl-4 mt-2">
        <!-- Подзадачи -->
        <div class="mt-2 space-y-2 border-l-2 border-gray-100 pl-3">
          <div v-for="childTask in childTasks" :key="childTask.id" class="mt-1">
            <TaskNode
                :task="childTask"
                :all-tasks="allTasks"
                :statusMap="statusMap"
                :paymentStatusMap="paymentStatusMap"
            />
          </div>
        </div>
      </div>
    </transition>

    <!-- Скрытый блок для формального использования классов (не отображается) чтоб успокоить линтер -->
    <div class="hidden" aria-hidden="true">
      <div class="expand-enter-active"></div>
      <div class="expand-leave-active"></div>
      <div class="expand-enter-from"></div>
      <div class="expand-leave-to"></div>
      <div class="expand-enter-to"></div>
      <div class="expand-leave-from"></div>
      <div class="fade-enter-active"></div>
      <div class="fade-leave-active"></div>
      <div class="fade-enter-from"></div>
      <div class="fade-leave-to"></div>
    </div>

  </div>
</template>

<style scoped>
.task-node {
  transition: background-color 0.2s ease;
}

/* Анимация раскрытия/сворачивания */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 300px; /* Достаточно большое значение для содержимого */
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 300px;
  opacity: 1;
  margin-top: 0.5rem;
}

/* Анимация появления/исчезновения модального окна */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>