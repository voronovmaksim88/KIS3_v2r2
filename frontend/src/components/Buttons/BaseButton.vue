// Buttons/BaseButton.vue
<script setup lang="ts">
import { computed } from 'vue';

// Интерфейс для входных параметров
interface Props {
  action: () => Promise<void>; // Функция, вызываемая при нажатии на кнопку
  text: string; // Текст кнопки
  style?: 'Primary' | 'Secondary' | 'Success' | 'Info' | 'Warn' | 'Help' | 'Danger' | 'Contrast'; // Опциональный стиль кнопки
}

// Определение пропсов со значением по умолчанию: Secondary
const props = withDefaults(defineProps<Props>(), {
  style: 'Secondary'
});

// Определяем классы стилей в зависимости от переданного `styleType`
const buttonClasses = computed(() => {
  const baseClasses = "w-full py-2 px-4 rounded transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-opacity-50 shadow-md"; // Добавляем тень

  const styleMap = {
    Primary: "bg-blue-700 text-white hover:bg-blue-500 focus:ring-blue-300",
    Secondary: "bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-100",
    Success: "bg-green-500 text-black hover:bg-green-600 focus:ring-green-300",
    Info: "bg-cyan-500 text-white hover:bg-cyan-600 focus:ring-cyan-300",
    Warn: "bg-yellow-500 text-black hover:bg-yellow-600 focus:ring-yellow-300",
    Help: "bg-purple-500 text-white hover:bg-purple-600 focus:ring-purple-300",
    Danger: "bg-red-500 text-white hover:bg-red-600 focus:ring-red-300",
    Contrast: "bg-black text-white hover:bg-gray-900 focus:ring-gray-500",
  };

  return `${baseClasses} ${styleMap[props.style]}`;
});
</script>

<template>
  <div class="flex items-center space-x-2">
    <button
        :class="buttonClasses"
        @click="action"
    >
      {{ text }}
    </button>
 </div>
</template>