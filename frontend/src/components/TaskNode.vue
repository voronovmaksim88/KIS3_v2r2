<!-- TaskNode.vue -->

<script setup lang="ts">
import { computed, ref } from 'vue';
import { typeTask} from "@/types/typeTask.ts";
import 'primeicons/primeicons.css';
import {formatFIO} from "@/utils/formatFIO.ts";
import TaskDetailView from './TaskDetailView.vue'; // Импортируем компонент с детальной информацией
import { useThemeStore } from "@/stores/storeTheme.ts"; // Импортируем хранилище темы

interface Props {
  task: typeTask;
  allTasks: typeTask[];
  statusMap: Record<number, string>;
  paymentStatusMap: Record<number, string>; // Добавляем карту статусов оплаты
}

// Получаем текущую тему из хранилища
const themeStore = useThemeStore();
const currentTheme = computed(() => themeStore.theme);

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

function getStatusBackgroundClass(statusId: number) {
  // Различные классы фона в зависимости от статуса и темы
  if (currentTheme.value === 'dark') {
    switch (statusId) {
      case 1: // "Не начата"
        return 'bg-gray-700'
      case 2: // "В работе"
        return 'bg-green-900'
      case 3: // "На паузе"
        return 'bg-purple-900'
      case 4: // "Завершена"
        return 'bg-blue-900'
      case 5: // "Отменена"
        return 'bg-red-900'
      default:
        return 'bg-gray-800' // По умолчанию темно-серый для темной темы
    }
  } else {
    // Светлая тема
    switch (statusId) {
      case 1: // "Не начата"
        return 'bg-gray-300'
      case 2: // "В работе"
        return 'bg-green-200'
      case 3: // "На паузе"
        return 'bg-purple-200'
      case 4: // "Завершена"
        return 'bg-blue-200'
      case 5: // "Отменена"
        return 'bg-red-200'
      default:
        return 'bg-gray-200' // По умолчанию светло-серый для светлой темы
    }
  }
}

// Получаем класс для текста в зависимости от темы
const getTextColorClass = computed(() => {
  return currentTheme.value === 'dark' ? 'text-white' : 'text-gray-800';
});

// Получаем класс для второстепенного текста (исполнитель) в зависимости от темы
const getSecondaryTextColorClass = computed(() => {
  return currentTheme.value === 'dark' ? 'text-gray-300' : 'text-gray-600';
});

// Получаем класс для границы подзадач в зависимости от темы
const getChildrenBorderClass = computed(() => {
  return currentTheme.value === 'dark' ? 'border-gray-700' : 'border-gray-300';
});

// Получаем класс для стрелки разворачивания в зависимости от темы
const getExpandIconClass = computed(() => {
  return currentTheme.value === 'dark'
      ? 'text-gray-300 border-gray-200' // изменено с border-gray-700
      : 'text-gray-700 border-gray-400';
});

// Получаем класс для рамки задачи в зависимости от темы
const getTaskBorderClass = computed(() => {
  return currentTheme.value === 'dark'
      ? 'border-gray-200'
      : 'border-gray-400';
});
</script>


<template>
  <div class="task-node border rounded-md p-1 transition-colors duration-300"
       :class="[
       getStatusBackgroundClass(task.status_id),
       getTaskBorderClass, // Добавить это
       {'hover-effect': !isExpanded},
     ]">

    <!-- Заголовок задачи (кликабельный для разворачивания, только если есть дочерние задачи) -->
    <div
        class="flex items-center justify-between pr-2 py-1 cursor-pointer"
        @click="toggleTaskDetails"
    >
      <!-- Левая часть - стрелка и название задачи -->
      <div class="flex items-center">
        <!-- Стрелка для разворачивания/сворачивания (если есть дочерние задачи) -->
        <span v-if="hasChildren"
              class="mr-1 border rounded-md px-2 py-1 transition-all duration-300 expand-icon-wrapper"
              :class="getExpandIconClass"
              @click.stop="toggleExpand"
        >
          <i class="pi pi-chevron-right transform transition-transform duration-300 expand-icon"
             :class="{ 'rotate-90': isExpanded }"></i>
        </span>
        <span v-else class="mr-2 w-4"></span> <!-- Пустое пространство для выравнивания -->

        <!-- Название задачи (кликабельное для открытия деталей) -->
        <div
            class="font-medium transition-colors duration-200"
            :class="getTextColorClass"
        >
          {{ task.name }}
        </div>
      </div>

      <!-- Правая часть - исполнитель -->
      <div v-if="task.executor"
           class="text-xs transition-colors duration-200"
           :class="getSecondaryTextColorClass">
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
        <div class="mt-2 space-y-2 border-l-2 pl-3 transition-colors duration-300"
             :class="getChildrenBorderClass">
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
      <div class="expand-enter-active expand-leave-active expand-enter-from expand-leave-to
                  expand-enter-to expand-leave-from fade-enter-active fade-leave-active
                  fade-enter-from fade-leave-to rotate-90 expand-leave-to fade-leave-active"></div>
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

/* Стили для плавного поворота стрелки */
.expand-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.expand-icon {
  display: inline-block;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-origin: center;
}

.rotate-90 {
  transform: rotate(90deg);
}

/* Улучшенный эффект при наведении на иконку разворачивания */
.expand-icon-wrapper:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>