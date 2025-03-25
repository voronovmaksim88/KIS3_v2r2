<!--src/components/TheMain.vue-->
<script setup lang="ts">
import TheLogin from "./TheLogin.vue"
import {useAuthStore} from '../stores/storeAuth.ts';
import {onMounted, watch} from 'vue'
import {computed, ref} from 'vue'

const props = defineProps({
  apiUrl: {
    type: String,
    required: true
  }
})

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated); // Использование геттера из Store
const isLoading = ref(true); // для отслеживания состояния загрузки

const emit = defineEmits([
  'btnKis',
  'btnYchetSnSkafov',
  'btnTestFastAPI',
  'btnCommercialOffer',
  'btnTestDataBase'])

function fnBtnKis() {
  emit('btnKis')
}

function fnBtnYchetSnSkafov() {
  emit('btnYchetSnSkafov')
}

function fnBtnTestFastAPI() {
  emit('btnTestFastAPI')
}

function fnBtnCommercialOffer() {
  emit('btnCommercialOffer')
}

function fnBtnTestDataBase() {
  emit('btnTestDataBase')
}


onMounted(async () => {
  try {
    isLoading.value = true;
    // Проверяем авторизацию при загрузке
    await authStore.checkAuth(props.apiUrl)

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

</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4">
    <h1 class="text-green-400 text-3xl mb-5 text-center">SibPLC-web</h1>

    <!-- Показываем форму логина, если пользователь не аутентифицирован -->
    <div
        v-if="!isAuthenticated && !isLoading"
        class="w-full max-w-[500px] mx-auto flex-1 flex flex-col transition-all duration-300 pb-32"
    >

      <TheLogin
          :api-url="apiUrl"
          class='fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-[500px]'
      />
    </div>


    <div v-if="isAuthenticated" class="flex flex-col w-full sm:w-1/2 md:w-1/3 lg:w-1/4 xl:w-1/6 space-y-4">

      <button class="btn btn-p" @click="fnBtnTestFastAPI">Тест FastAPI</button>
      <button class="btn btn-p" @click="fnBtnTestDataBase">Тест DataBase</button>
      <button class="btn btn-p" @click="fnBtnKis">КИС</button>
      <button class="btn btn-p" @click="fnBtnYchetSnSkafov">Учёт с/н шкафов</button>

      <button class="btn btn-s" @click="fnBtnCommercialOffer">Составление КП</button>
      <button class="btn btn-s" >Бланк ТЗ для ШАОВ</button>
      <button class="btn btn-s" >Расчёт стоимости ША</button>
      <button class="btn btn-s" >Подбор ПЛК</button>
    </div>
  </div>
</template>

<style scoped></style>
