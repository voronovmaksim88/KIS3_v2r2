<!--TheHeader-->
<script setup lang="ts">
import {usePagesStore} from "../stores/storePages.ts";
import {useAuthStore} from "../stores/storeAuth.ts";
import {useThemeStore} from "../stores/storeTheme.ts";
import {computed} from 'vue';

// Font Awesome
import {library} from '@fortawesome/fontawesome-svg-core';
import {faHouseChimney} from '@fortawesome/free-solid-svg-icons';
import {faSignOutAlt} from '@fortawesome/free-solid-svg-icons';
import {faUser} from '@fortawesome/free-solid-svg-icons';
import {faSun, faMoon} from '@fortawesome/free-solid-svg-icons';

import Button from 'primevue/button';
import ToggleTheme from "@/components/ToggleTheme.vue";

// Добавляем используемые иконки в библиотеку
library.add(faHouseChimney, faSignOutAlt, faUser, faSun, faMoon);

const props = defineProps({
  PageName: {
    type: String,
    default: "My Header" // Значение по умолчанию
  },
})

const pageStore = usePagesStore()
const authStore = useAuthStore();
const themeStore = useThemeStore();

// Создаем вычисляемое свойство для имени пользователя
const username = computed(() => authStore.username);
// Вычисляемое свойство для текущей темы
const currentTheme = computed(() => themeStore.theme);

function GoHome() {
  pageStore.setPage('main')
}

function Logout() {
  // Вызываем метод выхода из авторизационного хранилища.
  authStore.logout()
      .then(() => {
        // После успешного выхода переходим на главную страницу
        pageStore.setPage('main');
      })
      .catch(error => {
        console.error('Ошибка при выходе:', error);
      });
}

</script>

<template>
  <header
      class="app-header flex items-center justify-between p-3 shadow-md transition-colors duration-300 ease-in-out"
      :class="[
      currentTheme === 'dark'
        ? 'bg-gray-800 text-white shadow-gray-900/50'
        : 'bg-gray-100 text-gray-800 shadow-gray-300/50'
    ]"
  >
    <div class="flex items-center">
      <Button
          icon="pi pi-home"
          label="Home"
          severity="info"
          raised
          :onclick="GoHome"
      />
    </div>

    <p
        class="page-title text-4xl font-bold transition-colors duration-300"
        :class="[
        currentTheme === 'dark'
          ? 'text-green-300'
          : 'text-green-600'
      ]"
    >
      {{ props.PageName }}
    </p>

    <div class="flex items-center">
      <ToggleTheme />

      <Button
          icon="pi pi-user"
          :label="username"
          severity="info"
          raised
      />
    </div>
  </header>
</template>

<style scoped>
.app-header {
  border-bottom-width: 1px;
  border-bottom-color: v-bind('currentTheme === "dark" ? "rgba(75, 85, 99, 1)" : "rgba(229, 231, 235, 1)"');
}

.page-title {
  /* Разные эффекты тени для текста в зависимости от темы */
  text-shadow: v-bind('currentTheme === "dark" ? "0 0 8px rgba(52, 211, 153, 0.4)" : "0 0 1px rgba(5, 150, 105, 0.4)"');
  letter-spacing: 0.05em;
}

.username {
  /* Эффект свечения для имени активного пользователя в разных темах */
  box-shadow: v-bind('currentTheme === "dark" ? "0 0 5px rgba(255, 255, 255, 0.1)" : "0 0 5px rgba(0, 0, 0, 0.05)"');
}

/* Анимация для кнопки переключения темы */
.theme-toggle:active {
  transform: scale(0.95);
  transition: transform 0.1s;
}

/* Анимация для активного пользователя */
@keyframes pulse {
  0% {
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.8;
  }
}

.user-icon {
  display: inline-block;
  animation: v-bind('currentTheme === "dark" ? "pulse 2s infinite" : "none"');
}

/* Медиа-запрос для мобильной версии */
@media (max-width: 640px) {
  .page-title {
    font-size: 1.5rem; /* Делаем заголовок меньше на мобильных */
  }

  .app-header {
    padding: 0.75rem;
  }

  .username {
    padding: 0.25rem 0.5rem;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>