<script setup lang="ts">
import BaseButton from '@/components/Buttons/BaseButton.vue'
import {usePagesStore} from "../stores/storePages.ts";
import { useAuthStore } from "../stores/storeAuth.ts";
import { computed } from 'vue';

const props = defineProps({
  PageName: {
    type: String,
    default: "My Header" // Значение по умолчанию
  },
})


const pageStore = usePagesStore()
const authStore = useAuthStore();

// Создаем вычисляемое свойство для имени пользователя
const username = computed(() => authStore.username);

function GoHome() {
  pageStore.setPage('main')
}

function Logout() {
  // Вызываем метод выхода из авторизационного хранилища.
  // Заменяем URL на ваш API URL
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
  <div class="flex p-2 bg-gray-700">
    <BaseButton
        :text="'Home'"
        :action="GoHome"
        :style="'Primary'"
    />
    <p class="ml-auto text-green-400 text-4xl">{{ props.PageName }}</p>
    <p class="ml-auto text-white text-xl mr-4 mt-1">{{ username }}</p>
    <BaseButton
        :text="'logout'"
        :action="Logout"
        :style="'Secondary'"
    />
  </div>

</template>

<style scoped>

</style>