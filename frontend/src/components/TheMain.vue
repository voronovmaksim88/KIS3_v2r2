<!--src/components/TheMain.vue-->
<script setup lang="ts">
import { usePagesStore } from "../stores/storePages.ts";
import { useThemeStore } from "../stores/storeTheme";
import { computed, ref } from "vue"; // Добавим импорт ref
import BaseModal from "./BaseModal.vue"; // Добавим импорт BaseModal

// Получаем текущую тему из хранилища
const themeStore = useThemeStore();
const currentTheme = computed(() => themeStore.theme);

const pageStore = usePagesStore();

// Добавим состояние для отображения модального окна
const showModal = ref(false);

// Функции для управления модальным окном
const openModal = () => {
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};
</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center p-4"
       :class="[
         currentTheme === 'dark'
           ? 'bg-gray-800'
           : 'bg-gray-200'
       ]"
  >
    <div class="flex flex-col w-full sm:w-1/2 md:w-1/3 lg:w-1/4 xl:w-1/6 space-y-4">
      <button class="btn btn-p" @click="pageStore.setPage('box-serial-num')">Учёт с/н шкафов</button>
      <button class="btn btn-p" @click="pageStore.setPage('orders')">Заказы</button>
      <button class="btn btn-s">Задачи</button>
      <button class="btn btn-s">Тайминги</button>
      <button class="btn btn-p" @click="pageStore.setPage('test-fastapi')">Тест FastAPI</button>
      <button class="btn btn-p" @click="pageStore.setPage('test-db')">Тест базы данных</button>
      <button class="btn btn-s" @click="">Составление КП</button>
      <button class="btn btn-s">Бланк ТЗ для ШАОВ</button>
      <button class="btn btn-s">Расчёт стоимости ША</button>
      <button class="btn btn-s">Подбор ПЛК</button>

      <!-- Новая кнопка для открытия модального окна -->
      <button class="btn btn-p" @click="openModal">Открыть модальное окно</button>
    </div>

    <!-- Контейнер для модального окна с затемнением фона -->
    <div v-if="showModal"
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
         @click.self="closeModal">
      <BaseModal :name="'Тестовое модальное окно'" :onClose="closeModal">
        <div class="text-center">
          <p :class="currentTheme === 'dark' ? 'text-white' : 'text-gray-800'">
            Это тестовое содержимое модального окна для демонстрации компонента BaseModal.
          </p>
          <p :class="currentTheme === 'dark' ? 'text-gray-300' : 'text-gray-600'" class="mt-4">
            Вы можете закрыть это окно, нажав на крестик в правом верхнем углу или кликнув на затемненную область вокруг окна.
          </p>
          <button
              class="mt-6 px-4 py-2 rounded transition-colors duration-200"
              :class="currentTheme === 'dark'
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'"
              @click="closeModal">
            Закрыть
          </button>
        </div>
      </BaseModal>
    </div>
  </div>
</template>

<style scoped>

</style>