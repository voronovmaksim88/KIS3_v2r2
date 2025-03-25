<!--src/components/KIS.vue-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Определяем состояния компонента с помощью ref
const show_task = ref(false)
const show_orders = ref(false)
const countries = ref<Array<{id: number, name: string, code: string}>>([])


// Если хотите получить страны при монтировании компонента
onMounted(() => {

})

// Функции для обработки нажатия кнопок
function showOrders() {
  show_orders.value = true
  show_task.value = false
}

function showTasks() {
  show_task.value = true
  show_orders.value = false
}
</script>

<template>
  <div class="w-full h-screen flex flex-col items-center bg-gray-800 ">
    <div class="flex h-full flex-col w-1/6">
      <h1 class="text-green-400 text-3xl mb-5">SibPLC-KIS</h1>
      <button class="btn btn-p" @click="showOrders">Заказы</button>
      <button class="btn btn-p" @click="showTasks">Задачи</button>

      <p v-if="show_orders" class="text-green-200 text-xl"> тут тестово выведем все заказы </p>
      <p v-if="show_task" class="text-green-100 text-xl"> тут тестово выведем все задачи </p>
      <div v-if="show_task">
        <p v-for="country in countries" :key="country.id">{{ country.name }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>