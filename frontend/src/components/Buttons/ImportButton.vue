<script setup lang="ts">
import { ref, computed } from 'vue';

// Интерфейс для входных параметров
interface Props {
  importAction: () => Promise<void>; // Функция, вызываемая при импорте
  isImporting: boolean; // Флаг, указывающий, идет ли импорт
  importStatus: string; // Текущий статус импорта
  importResult: { status: string; added?: number; updated?: number; unchanged?: number } | null;
  importButtonText: string;
}

const props = defineProps<Props>();

// Локальное состояние текста кнопки
const importButtonState = ref(props.importButtonText);

// Следим за изменением статуса импорта
const importButtonClasses = computed((): string => {
  if (props.isImporting) {
    return 'bg-yellow-400 text-yellow-900 hover:bg-yellow-500 focus:ring-yellow-500 cursor-wait';
  }
  if (props.importStatus === 'Импорт успешен!') {
    return 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-700';
  }
  return 'bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-100';
});
</script>

<template>
  <div class="flex items-center space-x-2">
    <!-- Кнопка импорта -->
    <button
        class="w-full py-2 px-4 rounded font-bold transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-opacity-50"
        :class="importButtonClasses"
        @click="importAction"
        :disabled="isImporting"
    >
      {{ isImporting ? 'Импортирую...' : importButtonState }}
    </button>
  </div>
</template>