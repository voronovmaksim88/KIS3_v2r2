<script setup lang="ts">
import { computed } from 'vue';

// Интерфейс для входных параметров
interface Props {
  action: () => Promise<void>; // Функция, вызываемая при нажатии на кнопку
  text: string; // Текст кнопки
}

const props = defineProps<Props>();

// Следим за изменением статуса импорта
const importButtonClasses = computed((): string => {
  return 'bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-100';
});
</script>

<template>
  <div class="flex items-center space-x-2">
    <!-- Кнопка -->
    <button
        class="w-full py-2 px-4 rounded font-bold transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-opacity-50"
        :class="importButtonClasses"
        @click="action"
    >
      {{ props.text }}
    </button>
  </div>
</template>