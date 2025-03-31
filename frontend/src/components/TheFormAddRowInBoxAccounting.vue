// src/components/TheFormAddRowInBoxAccounting.vue
<script setup lang="ts">
import {faCircleCheck, faCircleXmark} from '@fortawesome/free-regular-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {library} from '@fortawesome/fontawesome-svg-core'
// Добавляем импорт onUnmounted
import {computed, onMounted, onUnmounted, ref} from "vue";
import {useFormsVisibilityStore} from '../stores/storeVisibilityForms';
import {usePeopleStore} from "@/stores/storePeople.ts";
import {useBoxAccountingStore} from "@/stores/storeBoxAccounting";
import {storeToRefs} from "pinia";
import {BoxAccountingCreateRequest} from "@/types/typeBoxAccounting";
import {useOrdersStore} from "@/stores/storeOrders";
import AutoComplete from 'primevue/autocomplete';
import {typeOrderSerial} from "@/types/typeOrder.ts";
import {Person} from "@/types/typePerson.ts";

const formsVisibilityStore = useFormsVisibilityStore();
const peopleStore = usePeopleStore();
const { error: peopleError } = storeToRefs(peopleStore);
const boxAccountingStore = useBoxAccountingStore();
const {boxes} = storeToRefs(boxAccountingStore);
const ordersStore = useOrdersStore();
const {orderSerials} = storeToRefs(ordersStore);

// Переменные для хранения специалистов по ролям
const schemDevelopers = ref<Person[]>([]);
const assemblers = ref<Person[]>([]);
const programmers = ref<Person[]>([]);
const testers = ref<Person[]>([]);

// Переменные для AutoComplete и их фильтрованных списков
const selectedOrder = ref<typeOrderSerial | null>(null);
const filteredOrders = ref<typeOrderSerial[]>([]);
const selectedShemDeveloper = ref<Person | null>(null);
const filteredShemDevelopers = ref<Person[]>([]);
const selectedAssembler = ref<Person | null>(null);
const filteredAssemblers = ref<Person[]>([]);
const selectedProgrammer = ref<Person | null>(null);
const filteredProgrammers = ref<Person[]>([]);
const selectedTester = ref<Person | null>(null);
const filteredTesters = ref<Person[]>([]);

library.add(faCircleCheck, faCircleXmark)
const newRowOk = ref(false)

// Начальное состояние для сброса newBox
const initialNewBoxState: BoxAccountingCreateRequest = {
  name: '',
  order_id: '',
  scheme_developer_id: '',
  assembler_id: '',
  programmer_id: undefined,
  tester_id: ''
};

// Используем клон начального состояния
const newBox = ref<BoxAccountingCreateRequest>({ ...initialNewBoxState });

const nextSerialNum = computed(() => {
  if (!boxes.value || boxes.value.length === 0) return 1;
  // Находим максимальный серийный номер и добавляем 1
  const maxSerialNum = Math.max(...boxes.value.map(box => box.serial_num));
  return maxSerialNum + 1;
});


function cancel() {
  formsVisibilityStore.isFormAddRowInBoxAccountingVisible = false
}

function addNewRow() {
  // Логика добавления строки...
  // После успешного добавления можно вызвать функцию очистки или скрыть форму
  // cleanupComponentState();
  // formsVisibilityStore.isFormAddRowInBoxAccountingVisible = false;
}

// === ЛОГИКА ЗАГРУЗКИ в onMounted ===
onMounted(async () => {
  console.log("Component Mounted - Starting data load...");

  // --- Загрузка и распределение специалистов ---
  try {
    console.log("Fetching active people...");
    const activePeople = await peopleStore.fetchActivePeople();

    // Очищаем списки перед заполнением (уже есть, но для ясности)
    schemDevelopers.value = [];
    assemblers.value = [];
    programmers.value = [];
    testers.value = [];

    if (activePeople && Array.isArray(activePeople)) {
      console.log(`Workspaceed ${activePeople.length} active people. Distributing by roles...`);
      activePeople.forEach(person => {
        if (person.can_be_scheme_developer) schemDevelopers.value.push(person);
        if (person.can_be_assembler) assemblers.value.push(person);
        if (person.can_be_programmer) programmers.value.push(person);
        if (person.can_be_tester) testers.value.push(person);
      });
      console.log('Distribution complete.');
    } else {
      console.warn("Не удалось загрузить активных специалистов или результат не массив.");
      if(peopleError.value) {
        console.error("People store error:", peopleError.value);
      }
    }
  } catch (error) {
    console.error("Критическая ошибка при загрузке и распределении специалистов:", error);
  }
  // --- Конец загрузки специалистов ---

  // --- Загрузка заказов ---
  try {
    console.log("Fetching order serials...");
    await ordersStore.fetchOrderSerials(2);
    console.log('Orders loaded:', orderSerials.value.length);
  } catch (error) {
    console.error('Failed to load orders:', error);
  }
  // --- Конец загрузки заказов ---

  console.log("Data loading finished.");
});

// === ЛОГИКА ОЧИСТКИ при Размонтировании ===
// Функция для очистки состояния компонента
function cleanupComponentState() {
  console.log("Cleaning up component state...");
  // Очистка списков специалистов
  schemDevelopers.value = [];
  assemblers.value = [];
  programmers.value = [];
  testers.value = [];

  // Очистка выбранных значений в AutoComplete
  selectedOrder.value = null;
  selectedShemDeveloper.value = null;
  selectedAssembler.value = null;
  selectedProgrammer.value = null;
  selectedTester.value = null;

  // Очистка отфильтрованных списков
  filteredOrders.value = [];
  filteredShemDevelopers.value = [];
  filteredAssemblers.value = [];
  filteredProgrammers.value = [];
  filteredTesters.value = [];

  // Сброс данных новой строки к начальному состоянию
  newBox.value = { ...initialNewBoxState };

  // Сброс флага успешной строки
  newRowOk.value = false;

  // Опционально: Очистка ошибок в сторах, если это нужно при уходе со страницы
  peopleStore.clearError();
  ordersStore.clearError();

  console.log("Component state cleaned.");
}

// Вызов функции очистки при размонтировании компонента
onUnmounted(() => {
  console.log("Component Unmounted - Triggering cleanup...");
  cleanupComponentState();

  // Сбрасываем видимость формы при уходе с компонента
  // (если форма не должна оставаться видимой при возвращении)
  formsVisibilityStore.isFormAddRowInBoxAccountingVisible = false;
  console.log("Form visibility reset.");
});
// === КОНЕЦ ЛОГИКИ ОЧИСТКИ ===


// --- Функции поиска и выбора для AutoComplete ---

function searchOrder(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredOrders.value = orderSerials.value.filter(order =>
      order.serial.toLowerCase().includes(query)
  );
}
function handleOrderSelect(event: { value: typeOrderSerial }) {
  newBox.value.order_id = event.value.serial;
  console.log('Selected order:', event.value);
}

function searchSchemDevelopers(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredShemDevelopers.value = schemDevelopers.value.filter(developer =>
      (developer.name && developer.name.toLowerCase().includes(query)) ||
      (developer.surname && developer.surname.toLowerCase().includes(query))
  );
}
function handleSchemDeveloperSelect(event: { value: Person }) {
  newBox.value.scheme_developer_id = event.value.uuid;
  console.log('Selected developer:', event.value);
}

function searchAssemblers(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredAssemblers.value = assemblers.value.filter(assembler =>
      (assembler.name && assembler.name.toLowerCase().includes(query)) ||
      (assembler.surname && assembler.surname.toLowerCase().includes(query))
  );
}
function handleAssemblerSelect(event: { value: Person }) {
  newBox.value.assembler_id = event.value.uuid;
  console.log('Selected assembler:', event.value);
}

function searchTesters(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredTesters.value = testers.value.filter(person =>
      (person.name && person.name.toLowerCase().includes(query)) ||
      (person.surname && person.surname.toLowerCase().includes(query))
  );
}
function handleTesterSelect(event: { value: Person }) {
  newBox.value.tester_id = event.value.uuid;
  console.log('Selected tester:', event.value);
}

function searchProgrammers(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredProgrammers.value = programmers.value.filter(person =>
      (person.name && person.name.toLowerCase().includes(query)) ||
      (person.surname && person.surname.toLowerCase().includes(query))
  );
}
function handleProgrammerSelect(event: { value: Person }) {
  newBox.value.programmer_id = event.value.uuid;
  console.log('Selected programmer:', event.value);
}

function formatPersonName(person: Person): string {
  if (!person) return '';
  const s = person.surname || '';
  const n = person.name?.[0] || '';
  const o = person.patronymic?.[0] || '';
  return `${s}${n ? ' ' + n + '.' : ''}${o ? o + '.' : ''}`.trim();
}

</script>

<template>
  <div class="w-full bg-gray-700 p-4 rounded-lg mb-4">
    <h2 class="text-xl font-bold mb-4">Добавление новой записи</h2>

    <div v-if="peopleStore.error" class="w-full bg-red-500 text-white p-4 rounded mb-4">
      {{ peopleStore.error }}
    </div>

    <div v-if="ordersStore.error" class="w-full bg-red-500 text-white p-4 rounded mb-4">
      {{ ordersStore.error }}
    </div>

    <div v-if="peopleStore.isLoading || ordersStore.isLoading" class="w-full flex justify-center my-4">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-if="!peopleStore.isLoading && !ordersStore.isLoading && !peopleStore.error && !ordersStore.error" class="w-full">
      <div class="overflow-x-auto">
        <table class="min-w-full bg-gray-700 rounded-lg mb-4 table-fixed">
          <colgroup>
            <col style="width: 6%">  <!-- С/Н -->
            <col style="width: 15%"> <!-- Название -->
            <col style="width: 18%"> <!-- Заказ -->
            <col style="width: 16%"> <!-- Разработчик схемы -->
            <col style="width: 16%"> <!-- Сборщик -->
            <col style="width: 16%"> <!-- Программист -->
            <col style="width: 16%"> <!-- Тестировщик -->
          </colgroup>
          <thead>
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
          <tr class="border-t border-gray-600">

            <td class="px-4 py-2">
              <div class="bg-gray-600 px-2 py-1 rounded">
                <p> {{ nextSerialNum }}</p>
              </div>
            </td>

            <td class="px-4 py-2">
              <input
                  type="text"
                  v-model="newBox.name"
                  class="w-full bg-gray-600 px-2 py-1 rounded"
                  placeholder="Введите название"
              />
            </td>

            <td>
              <AutoComplete
                  v-model="selectedOrder"
                  dropdown
                  :suggestions="filteredOrders"
                  :forceSelection="true"
                  @complete="searchOrder($event)"
                  placeholder="Выберите номер заказа"
                  optionLabel="serial"
                  @item-select="handleOrderSelect"
                  size="small"
              />
            </td>

            <td>
              <AutoComplete
                  v-model="selectedShemDeveloper"
                  dropdown
                  :suggestions="filteredShemDevelopers"
                  @complete="searchSchemDevelopers"
                  :forceSelection="true"
                  placeholder="Выберите разработчика"
                  @item-select="handleSchemDeveloperSelect"
                  size="small"
                  :optionLabel="formatPersonName"
              >
                <template #option="slotProps">
                  {{ slotProps.option.surname }} {{ slotProps.option.name?.[0] || '' }}.{{ slotProps.option.patronymic?.[0] || '' }}.
                </template>
              </AutoComplete>
            </td>


            <td>
              <AutoComplete
                  v-model="selectedAssembler"
                  dropdown
                  :suggestions="filteredAssemblers"
                  @complete="searchAssemblers"
                  :forceSelection="true"
                  placeholder="Выберите сборщика"
                  @item-select="handleAssemblerSelect"
                  size="small"
                  :optionLabel="formatPersonName"
              >
                <template #option="slotProps">
                  {{ slotProps.option.surname }} {{ slotProps.option.name?.[0] || '' }}.{{ slotProps.option.patronymic?.[0] || '' }}.
                </template>
              </AutoComplete>
            </td>

            <td>
              <AutoComplete
                  v-model="selectedProgrammer"
                  dropdown
                  :suggestions="filteredProgrammers"
                  @complete="searchProgrammers"
                  :forceSelection="true"
                  placeholder="Выберите программиста"
                  @item-select="handleProgrammerSelect"
                  size="small"
                  :optionLabel="formatPersonName"
              >
                <template #option="slotProps">
                  {{ slotProps.option.surname }} {{ slotProps.option.name?.[0] || '' }}.{{ slotProps.option.patronymic?.[0] || '' }}.
                </template>
              </AutoComplete>
            </td>

            <td>
              <AutoComplete
                  v-model="selectedTester"
                  dropdown
                  :suggestions="filteredTesters"
                  @complete="searchTesters"
                  :forceSelection="true"
                  placeholder="Выберите тестировщика"
                  @item-select="handleTesterSelect"
                  size="small"
                  :optionLabel="formatPersonName"
              >
                <template #option="slotProps">
                  {{ slotProps.option.surname }} {{ slotProps.option.name?.[0] || '' }}.{{ slotProps.option.patronymic?.[0] || '' }}.
                </template>
              </AutoComplete>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <div class="flex justify-end space-x-2">
        <button
            class="flex items-center justify-center px-2 py-2 border-gray-300 bg-gradient-to-tr from-gray-600
          to-gray-800 rounded min-w-[40px] md:min-w-[120px] transition-all duration-200"
            @click="cancel"
        >
          <FontAwesomeIcon
              :icon="['far', 'circle-xmark']"
              class="w-6 h-6 text-red-500 md:mr-2"
          />
          <span class="hidden md:inline">Отмена</span>
        </button>

        <button
            class="flex items-center justify-center px-2 py-2 border-gray-300 bg-gradient-to-tr from-gray-600
           to-gray-800 rounded min-w-[40px] md:min-w-[120px] transition-all duration-200"
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
  </div>
</template>

<style scoped>
/* ... ваши стили ... */
</style>

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

/* Стили для таблицы с фиксированной шириной */
.table-fixed {
  table-layout: fixed;
  width: 100%;
}
</style>