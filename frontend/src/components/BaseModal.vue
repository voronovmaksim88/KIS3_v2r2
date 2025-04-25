<!-- BaseModal.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import { useThemeStore } from "@/stores/storeTheme.ts";
import 'primeicons/primeicons.css'; // Добавляем импорт иконок, если он не глобально доступен

interface Props {
  onClose?: () => void;
  name: string;
}

const props = defineProps<Props>();

// Получаем текущую тему из хранилища
const themeStore = useThemeStore();
const currentTheme = computed(() => themeStore.theme);

// Вычисляемые свойства для цветов в зависимости от темы
const bgMainClass = computed(() => currentTheme.value === 'dark' ? 'bg-gray-800' : 'bg-white');
const bgHeaderClass = computed(() => currentTheme.value === 'dark' ? 'bg-gray-700' : 'bg-gray-100');
const textMainClass = computed(() => currentTheme.value === 'dark' ? 'text-white' : 'text-gray-800');
const borderClass = computed(() => currentTheme.value === 'dark' ? 'border-gray-700' : 'border-gray-200');
</script>

<template>
  <div :class="[bgMainClass, 'rounded-lg shadow-lg overflow-hidden max-w-4xl w-full mx-auto border transition-colors duration-300', borderClass]">
    <!-- Шапка с названием и кнопкой закрытия -->
    <div :class="[bgHeaderClass, 'px-6 py-4 flex justify-between items-center transition-colors duration-300']">
      <h2 :class="[textMainClass, 'text-xl font-semibold truncate transition-colors duration-300']">{{ props.name }}</h2>
      <button
          v-if="onClose"
          @click="onClose"
          :class="[currentTheme === 'dark' ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-800']"
          class="transition-colors duration-200"
          aria-label="Закрыть"
      >
        <i class="pi pi-times text-xl"></i>
      </button>
    </div>

    <!-- Содержимое модального окна -->
    <div class="p-6">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
/* Добавим плавные переходы для эффектов наведения */
button {
  transition: all 0.2s ease;
}
</style>