<!--App.vue-->
<script setup lang="ts">

import TheMain from "./components/TheMain.vue";
import BoxSerialNum from "./components/TheBoxSerialNum.vue";
//import CommercialOffer from "./components/TheCommercialOffer.vue";
import TheTestFastAPI from "./components/Test_FastAPI/The_Test_FastAPI.vue";
import TheTestDataBase from "./components/TestDataBase/TheTestDataBase.vue";
import TheHeader from "@/components/TheHeader.vue";
import {usePagesStore} from "./stores/storePages.ts";
import {computed, onMounted, ref, watch} from 'vue';
import {useAuthStore} from "./stores/storeAuth.ts";
import TheLogin from "@/components/TheLogin.vue";

const apiUrl = ref<string>('');

onMounted(() => {
  if (!import.meta.env.VITE_API_URL) {
    console.error('VITE_API_URL не определен в переменных окружения');
  }
  apiUrl.value = import.meta.env.VITE_API_URL;
});


const pageStore = usePagesStore()
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated); // Использование геттера из Store
const isLoading = ref(false); // для отслеживания состояния загрузки

onMounted(async () => {
  try {
    isLoading.value = true;
    // Проверяем авторизацию при загрузке
    await authStore.checkAuth()

    // Если пользователь авторизован, загружаем данные
    if (authStore.isAuthenticated) {
      await Promise.all([
        // тут потом надо загрузить проекты и другие данные
      ])
    }
  } catch (error) {
    console.error('Error checking auth:', error)
    // В случае ошибки явно устанавливаем состояние неавторизованного пользователя
    authStore.setAuthState(false)
  } finally {
    isLoading.value = false;
  }
})

// Следим за изменением состояния аутентификации
watch(
    () => authStore.isAuthenticated,
    (newValue) => {
      if (!newValue) {
        // тут потом надо почистить данные если пользователь разлогинился
      }
    }
)

const currentPageLabel = computed(() => {
  const tab = pageStore.tabs.find(tab => tab.id === pageStore.selectedPage);
  return tab ? tab.label : pageStore.selectedPage; // Если не найден, вернёт id
});

</script>

<template>
  <!-- Показываем форму логина, если пользователь не аутентифицирован -->
  <div
      v-if="!isAuthenticated "
      class="w-full min-h-screen bg-gray-800 p-4"
  >

    <TheLogin
        :api-url="apiUrl"
        class='fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-[500px]'
    />
  </div>

  <div v-if="isAuthenticated">
    <TheHeader
        :PageName='currentPageLabel'
    />

    <TheMain
        v-if="pageStore.selectedPage == 'main'"
    />
    <BoxSerialNum v-if="pageStore.selectedPage == 'box-serial-num'"/>
    <TheTestFastAPI v-if="pageStore.selectedPage == 'test-fastapi'"/>
    <TheTestDataBase v-if="pageStore.selectedPage == 'test-db'"/>
    <!--  <CommercialOffer  v-if="" />-->
  </div>

</template>

<style></style>
