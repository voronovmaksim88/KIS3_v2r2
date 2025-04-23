<!--TheHeader-->
<script setup lang="ts">
import BaseButton from '@/components/Buttons/BaseButton.vue'
import {usePagesStore} from "../stores/storePages.ts";
import {useAuthStore} from "../stores/storeAuth.ts";
import {useThemeStore} from "../stores/storeTheme.ts";
import {computed} from 'vue';

// Font Awesome
import {library} from '@fortawesome/fontawesome-svg-core';
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome';
import {faHouseChimney} from '@fortawesome/free-solid-svg-icons';
import {faSignOutAlt} from '@fortawesome/free-solid-svg-icons';
import {faUser} from '@fortawesome/free-solid-svg-icons';
import {faSun, faMoon} from '@fortawesome/free-solid-svg-icons';

import Button from 'primevue/button';

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

function toggleTheme() {
  themeStore.toggleTheme();
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
      <Button label="Submit" />

      <BaseButton
          :text="''"
          :action="GoHome"
          :style="currentTheme === 'dark' ? 'Primary' : 'Secondary'"
      >
        <!-- Добавляем иконку как слот перед текстом -->
        <template #prepend>
          <font-awesome-icon
              :icon="['fas', 'house-chimney']"
              class="mr-2 transition-colors duration-300 "
              :class="[
              currentTheme === 'dark' ? 'text-blue-300' : 'text-blue-100'
            ]"
          />
        </template>

        <!-- Показываем текст только на больших экранах -->
        <template #default>
          <span class="hidden sm:inline">Home</span>
        </template>
      </BaseButton>
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

    <div class="flex items-center gap-4">
      <!-- Переключатель темы с иконками Font Awesome -->
      <button
          @click="toggleTheme"
          class="theme-toggle flex items-center justify-center px-3 py-2 rounded-lg transition-all duration-300"
          :class="[
          currentTheme === 'dark'
            ? 'bg-gray-500 hover:bg-gray-400 text-yellow-300 hover:text-yellow-200'
            : 'bg-blue-200 hover:bg-blue-300 text-blue-800 hover:text-blue-900'
        ]"
          :title="
          currentTheme === 'dark'
            ? 'Переключить на светлую тему'
            : 'Переключить на темную тему'
          "
      >
        <font-awesome-icon
            :icon="['fas', currentTheme === 'dark' ? 'moon' : 'sun']"
            class="text-xl mr-2 transition-all duration-300"
            :class="[
            currentTheme === 'dark'
              ? 'text-yellow-300 rotate-0'
              : 'text-yellow-600 rotate-90'
          ]"
        />
        <span class="hidden sm:inline text-sm font-medium">
          {{
            currentTheme === 'dark' ? 'Темная' : 'Светлая'
          }}
        </span>
      </button>

      <!-- Имя пользователя с разным стилем в зависимости от темы -->
      <div
          class="username px-3 py-2 rounded-lg transition-colors duration-300"
          :class="[
          currentTheme === 'dark'
            ? 'bg-gray-500 text-gray-200'
            : 'bg-gray-300 text-gray-700'
        ]"
      >
        <span class="user-icon mr-2">
          <font-awesome-icon
              :icon="['fas', 'user']"
              class="transition-colors duration-300"
              :class="[currentTheme === 'dark' ? 'text-blue-300' : 'text-blue-500']"
          />
        </span>
        <span class="font-medium">{{ username }}</span>
      </div>

      <!-- Кнопка выхода с иконкой -->
      <BaseButton
          :text="''"
          :action="Logout"
          :style="currentTheme === 'dark' ? 'Secondary' : 'Danger'"
      >
        <template #prepend>
          <font-awesome-icon
              :icon="['fas', 'sign-out-alt']"
              class="mr-2 transition-colors duration-300"
              :class="[currentTheme === 'dark' ? 'text-white' : 'text-red-100']"
          />
        </template>

        <template #default>
          <span class="hidden sm:inline">logout</span>
        </template>
      </BaseButton>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  border-bottom-width: 1px;
  border-bottom-style: solid;
  border-bottom-color: v-bind('currentTheme === "dark" ? "rgba(75, 85, 99, 1)" : "rgba(229, 231, 235, 1)"');
}

.page-title {
  /* Разные эффекты тени для текста в зависимости от темы */
  text-shadow: v-bind('currentTheme === "dark" ? "0 0 8px rgba(52, 211, 153, 0.4)" : "0 0 1px rgba(5, 150, 105, 0.4)"');
  letter-spacing: 0.05em;
}

.theme-toggle {
  /* Добавляем эффект свечения для кнопки в темной теме */
  box-shadow: v-bind('currentTheme === "dark" ? "0 0 10px rgba(252, 211, 77, 0.2)" : "none"');
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