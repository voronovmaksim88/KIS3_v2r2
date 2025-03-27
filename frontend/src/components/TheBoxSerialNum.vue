<script setup lang="ts">
import {onMounted, ref} from 'vue';
import {useBoxAccountingStore} from '../stores/storeBoxAccounting';
import {useFormsVisibilityStore} from '../stores/storeVisibilityForms';
import {storeToRefs} from 'pinia';
import TheFormAddRowInBoxAccounting from "@/components/TheFormAddRowInBoxAccounting.vue";
import BaseButton from "@/components/Buttons/BaseButton.vue";



const boxAccountingStore = useBoxAccountingStore();
const formsVisibilityStore = useFormsVisibilityStore();

const {boxes, isLoading, error, pagination} = storeToRefs(boxAccountingStore);

// URL вашего API-сервера
const apiUrl = ref(import.meta.env.VITE_API_URL || 'http://localhost:8000');

// Загрузка данных при монтировании компонента
onMounted(async () => {
  await boxAccountingStore.fetchBoxes(apiUrl.value);
  console.log('Boxes loaded:', boxes.value.length);
});

function addNewRow() {
  formsVisibilityStore.isFormAddRowInBoxAccountingVisible = true
}

</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800 p-4 text-white">

    <!-- Показываем индикатор загрузки -->
    <div v-if="isLoading" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <!-- Показываем ошибку, если она есть -->
    <div v-if="error" class="w-full bg-red-500 text-white p-4 rounded mb-4">
      {{ error }}
    </div>

    <!-- Показываем форму добавления если надо -->
    <!-- Анимация появления и исчезновения формы -->
    <transition name="fade-slide">
      <TheFormAddRowInBoxAccounting
          v-if="formsVisibilityStore.isFormAddRowInBoxAccountingVisible"
      />
    </transition>

    <!-- Показываем данные -->
    <div v-if="!isLoading && boxes.length > 0" class="w-full">
      <div class="overflow-x-auto">
        <table class="min-w-full bg-gray-700 rounded-lg">
          <thead>
          <tr>
            <th colspan="7" class="px-2 py-2 text-center bg-gray-600 ">
              <div  class="px-1 py-1 bg-gray-600 flex justify-end items-center">
              <BaseButton
                  :action="addNewRow"
                  :text="'Добавить'"
                  :style="'Success'"
              />
              </div>
            </th>
          </tr>
          <tr>
            <th class="px-4 py-2 text-left">С/Н</th>
            <th class="px-4 py-2 text-left">Название</th>
            <th class="px-4 py-2 text-left">Заказ</th>
            <th class="px-4 py-2 text-left">Разработчик схемы</th>
            <th class="px-4 py-2 text-left">Сборщик</th>
            <th class="px-4 py-2 text-left">Программист</th>
            <th class="px-4 py-2 text-left">Тестировщик</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="box in boxes" :key="box.serial_num" class="border-t border-gray-600">
            <td class="px-4 py-2">{{ box.serial_num }}</td>
            <td class="px-4 py-2">{{ box.name }}</td>
            <td class="px-4 py-2">{{ box.order_id }}</td>
            <td class="px-4 py-2">
              {{
                box.scheme_developer.surname + ' ' + box.scheme_developer.name[0] + '.'
                + box.scheme_developer.patronymic[0] + '.'
              }}
            </td>
            <td class="px-4 py-2">
              {{
                box.assembler.surname + ' ' + box.assembler.name[0] + '.'
                + box.assembler.patronymic[0] + '.'
              }}
            </td>
            <td class="px-4 py-2">
              <template v-if="box.programmer">
                {{ box.programmer.surname + ' ' + box.programmer.name[0] + '.' + box.programmer.patronymic[0] + '.' }}
              </template>
              <template v-else>
                ---
              </template>
            </td>
            <td class="px-4 py-2">
              {{
                box.tester.surname + ' ' + box.tester.name[0] + '.'
                + box.tester.patronymic[0] + '.'
              }}
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Пагинация -->
      <div class="flex justify-between items-center mt-4">
        <span>
          Показано {{ boxes.length }} из {{ pagination.total }} записей
          (Страница {{ pagination.page }} из {{ pagination.pages }})
        </span>
        <div class="flex space-x-2">
          <button
              @click="boxAccountingStore.changePage(apiUrl, pagination.page - 1)"
              :disabled="pagination.page <= 1"
              class="px-4 py-2 bg-blue-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Prev
          </button>
          <button
              @click="boxAccountingStore.changePage(apiUrl, pagination.page + 1)"
              :disabled="pagination.page >= pagination.pages"
              class="px-4 py-2 bg-blue-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Сообщение, если данных нет -->
    <div v-if="!isLoading && boxes.length === 0" class="w-full text-center p-8">
      No boxes found. Please add some boxes to get started.
    </div>
  </div>

  <!-- Невидимый элемент, чтобы линтер не жаловался -->
  <div v-if="false" class="fade-slide-enter-active fade-slide-leave-active fade-slide-enter-from fade-slide-leave-to">

  </div>
</template>

<style scoped>
/* Анимация появления и исчезновения */
/* stylelint-disable */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease-in-out;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
/* stylelint-enable */


/* Стиль таблицы */
table {
  border-collapse: separate;
  border-spacing: 0;
}

th, td {
  border-bottom: 1px solid #4b5563;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: rgba(55, 65, 81, 0.7);
}
</style>