<!-- ToggleTheme -->
<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useThemeStore } from "../stores/storeTheme";

// Получаем хранилище темы из Pinia
const themeStore = useThemeStore();

// Вычисляемое свойство для определения темной темы
const isDarkTheme = computed(() => themeStore.theme === 'dark');

// Функция для переключения темы
function toggleThemeHandler() {
  themeStore.toggleTheme();
  updateDocumentClass();
}

// Функция для обновления класса на элементе document
function updateDocumentClass() {
  document.documentElement.classList.toggle('my-app-dark', isDarkTheme.value);
}

// При монтировании компонента синхронизируем состояние DOM с хранилищем
onMounted(() => {
  // Инициализируем класс на document в соответствии с текущей темой
  updateDocumentClass();

  // Проверяем наличие сохраненной темы в localStorage
  const storedTheme = localStorage.getItem('theme');

  if (storedTheme === 'dark' || storedTheme === 'light') {
    // Если тема сохранена и отличается от текущей, обновляем хранилище
    if (storedTheme !== themeStore.theme) {
      themeStore.setTheme(storedTheme as 'light' | 'dark');
      updateDocumentClass();
    }
  } else {
    // Если тема не сохранена, определяем по предпочтениям системы
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if ((prefersDark && themeStore.theme !== 'dark') || (!prefersDark && themeStore.theme !== 'light')) {
      themeStore.setTheme(prefersDark ? 'dark' : 'light');
      updateDocumentClass();
    }
  }
});
</script>


<template>
  <!-- Переключатель в стиле слайдера с двумя иконками -->
  <div class="theme-toggle-wrapper">
    <button
        @click="toggleThemeHandler"
        class="theme-toggle-slider flex items-center relative rounded-full transition-all duration-500 p-1"
        :class="[
        isDarkTheme
          ? 'bg-gray-700 hover:bg-gray-600'
          : 'bg-blue-200 hover:bg-blue-300'
      ]"
        aria-label="Переключить тему"
    >
      <!-- Движущийся индикатор текущей темы -->
      <div
          class="slider-indicator absolute rounded-full transition-all duration-500 transform"
          :class="[
          isDarkTheme
            ? 'translate-x-full bg-blue-900'
            : 'translate-x-0 bg-yellow-400'
        ]"
      ></div>

      <!-- Солнце (светлая тема) -->
      <div class="icon-container flex items-center justify-center relative z-10">
        <i class="pi pi-sun" :class="isDarkTheme ? 'text-yellow-500' : 'text-gray-800'"></i>
      </div>

      <!-- Луна (темная тема) -->
      <div class="icon-container flex items-center justify-center relative z-10">
        <i class="pi pi-moon" :class="isDarkTheme ? 'text-white' : 'text-gray-500'"></i>
      </div>
    </button>
  </div>
</template>


<style scoped>
.theme-toggle-wrapper {
  position: relative;
  margin: 0 0.5rem;
}

.theme-toggle-slider {
  width: 90px;
  height: 44px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.icon-container {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: color 0.3s;
}

.slider-indicator {
  width: 40px;
  height: 40px;
  left: 2px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* Эффект при наведении */
.theme-toggle-slider:hover {
  filter: brightness(1.1);
}

/* Эффект при нажатии */
.theme-toggle-slider:active {
  transform: scale(0.98);
  transition: transform 0.1s;
}

/* Адаптивность для маленьких экранов */
@media (max-width: 640px) {
  .theme-toggle-slider {
    width: 80px;
    height: 40px;
  }

  .icon-container {
    width: 36px;
    height: 36px;
    font-size: 1.125rem;
  }

  .slider-indicator {
    width: 36px;
    height: 36px;
  }
}
</style>