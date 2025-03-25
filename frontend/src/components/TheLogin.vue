<!--TheLogin.vue-->
<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/storeAuth'

const props = defineProps({
  apiUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['auth-success'])
const authStore = useAuthStore()

// Состояние для хранения введенных пользователем данных
const credentials = ref({
  username: '',
  password: ''
})

// Состояние для ошибок
const error = ref('')
const isLoading = ref(false)

// Функция для авторизации
async function login() {
  if (!credentials.value.username || !credentials.value.password) {
    error.value = 'Пожалуйста, заполните все поля'
    return
  }

  try {
    isLoading.value = true
    error.value = ''

    // Используем метод login из authStore
    const success = await authStore.login(
        credentials.value.username,
        credentials.value.password,
        props.apiUrl
    )

    if (success) {
      // Очищаем поля формы
      credentials.value.username = ''
      credentials.value.password = ''

      // Отправляем событие успешной авторизации
      emit('auth-success', credentials.value)
    } else {
      error.value = 'Неверное имя пользователя или пароль'
    }
  } catch (e) {
    console.error('Login error:', e)
    error.value = 'Ошибка при попытке входа'
  } finally {
    isLoading.value = false
  }
}

</script>

<template>
  <div class="p-4">
    <div class="flex flex-col space-y-4 border-gray-500 border rounded-md p-3">
      <h2 class="text-white text-xl">Вход в систему</h2>

      <input
          class="rounded-md px-2 py-2"
          type="text"
          v-model="credentials.username"
          placeholder="Имя пользователя"
          :disabled="isLoading"
      />

      <input
          class="rounded-md px-2 py-2"
          type="password"
          v-model="credentials.password"
          placeholder="Пароль"
          :disabled="isLoading"
          @keyup.enter="login"
      />

      <div
          v-if="error"
          class="text-red-500 text-sm"
      >
        {{ error }}
      </div>

      <button
          @click="login"
          :disabled="isLoading"
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isLoading">Вход...</span>
        <span v-else>Войти</span>
      </button>
    </div>
  </div>
</template>

<style scoped>

</style>