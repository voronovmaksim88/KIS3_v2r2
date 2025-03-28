<script setup lang="ts">
import {faCircleCheck} from '@fortawesome/free-regular-svg-icons'  // иконка птичка
import {faCircleXmark} from '@fortawesome/free-regular-svg-icons'  // иконка крестик в кружочке
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {library} from '@fortawesome/fontawesome-svg-core'
import {onMounted, ref} from "vue";
import {useFormsVisibilityStore} from '../stores/storeVisibilityForms';
import {usePeopleStore} from "@/stores/storePeople.ts";
import {storeToRefs} from "pinia";

const formsVisibilityStore = useFormsVisibilityStore();
const peopleStore = usePeopleStore();
const {people, isLoading, error} = storeToRefs(peopleStore);

library.add(faCircleCheck, faCircleXmark) // Добавляем иконки в библиотеку
const newRowOk = ref(false)

function cancel(){
  formsVisibilityStore.isFormAddRowInBoxAccountingVisible = false
}

function addNewRow(){
}

// Загрузка данных при монтировании компонента
onMounted(async () => {
  try {
    await peopleStore.fetchPeople();
    console.log('People loaded:', people.value.length);
    console.log('isLoading:', isLoading.value);
    console.log('error:', error.value);
  } catch (error) {
    console.error('Failed to load people:', error);
  }
});
</script>

<template>
  <!-- Форма для добавления новой записи -->
  <div class="w-full bg-gray-700 p-4 rounded-lg mb-4">
    <h2 class="text-xl font-bold mb-4">Добавить новую запись</h2>

    <!-- Контейнер для кнопок -->
    <div class="flex justify-end space-x-2">
      <!-- Кнопка "Отмена" -->
      <button
          class="flex items-center justify-center px-2 py-2 border-gray-300 bg-gradient-to-tr from-gray-600 to-gray-800 rounded
                 min-w-[40px] md:min-w-[120px] transition-all duration-200"
          @click="cancel"
      >
        <FontAwesomeIcon
            :icon="['far', 'circle-xmark']"
            class="w-6 h-6 text-red-500 md:mr-2"
        />
        <span class="hidden md:inline">Отмена</span>
      </button>

      <!-- Кнопка "Записать" -->
      <button
          class="flex items-center justify-center px-2 py-2 border-gray-300 bg-gradient-to-tr from-gray-600 to-gray-800 rounded
                 min-w-[40px] md:min-w-[120px] transition-all duration-200"
          @click="addNewRow"
      >
        <FontAwesomeIcon
            :icon="['far', 'circle-check']"
            :class="[newRowOk ? 'w-6 h-6 text-green-500 md:mr-2' : 'w-6 h-6 text-gray-300 md:mr-2']"
        />
        <span class="hidden md:inline">Записать</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
button {
  border-radius: 8px;
  border: 1px solid;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: lightgray;
  cursor: pointer;
  transition: border-color 0.25s;
}

button:hover {
  border-color: #646cff;
}

button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}
</style>