<!-- src/components/TheFormAddRowInBoxAccounting.vue-->
<script setup lang="ts">
import {faCircleCheck} from '@fortawesome/free-regular-svg-icons'  // иконка птичка
import {faCircleXmark} from '@fortawesome/free-regular-svg-icons'  // иконка крестик в кружочке
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {library} from '@fortawesome/fontawesome-svg-core'
import {computed, onMounted, ref} from "vue";
import {useFormsVisibilityStore} from '../stores/storeVisibilityForms';
import {usePeopleStore} from "@/stores/storePeople.ts";
import {useBoxAccountingStore} from "@/stores/storeBoxAccounting"; // Импортируем стор для учёта шкафов
import {storeToRefs} from "pinia";
import {BoxAccountingCreateRequest} from "@/types/typeBoxAccounting";
import {useOrdersStore} from "@/stores/storeOrders";
import AutoComplete from 'primevue/autocomplete';
import {typeOrderSerial} from "@/types/typeOrder.ts";
import {Person} from "@/types/typePerson.ts";


const formsVisibilityStore = useFormsVisibilityStore();
const peopleStore = usePeopleStore();
const {people, isLoading, error} = storeToRefs(peopleStore);
const boxAccountingStore = useBoxAccountingStore(); // Используем стор для шкафов
const {boxes} = storeToRefs(boxAccountingStore);
const ordersStore = useOrdersStore();
const {orderSerials} = storeToRefs(ordersStore);

// 🧠 Добавляем переменные для хранения специалистов по ролям
const schemDevelopers = ref<Person[]>([]);
const assemblers = ref<Person[]>([]);
const programmers = ref<Person[]>([]);
const testers = ref<Person[]>([]);

library.add(faCircleCheck, faCircleXmark) // Добавляем иконки в библиотеку
const newRowOk = ref(false)

// Создаем объект для новой записи, реактивную ссылку с явным указанием типа
const newBox = ref<BoxAccountingCreateRequest>({
  name: '',
  order_id: '',
  scheme_developer_id: '',
  assembler_id: '',
  programmer_id: undefined, // или null в зависимости от того, что ожидает ваш бэкенд
  tester_id: ''
})

// Вычисляем следующий серийный номер
const nextSerialNum = computed(() => {
  if (!boxes.value || boxes.value.length === 0) return 1;

  // Находим максимальный серийный номер и добавляем 1
  const maxSerialNum = Math.max(...boxes.value.map(box => box.serial_num));
  return maxSerialNum + 1;
});

// Для AutoComplete
const selectedOrder = ref(null);
const filteredOrders = ref<typeOrderSerial[]>([]);

function cancel() {
  formsVisibilityStore.isFormAddRowInBoxAccountingVisible = false
}

function addNewRow() {
}

// Загрузка данных при монтировании компонента
onMounted(async () => {
  // Загружаем список активных специалистов
  try {
    schemDevelopers.value = await peopleStore.fetchActiveSpecialists("developer") || []
    assemblers.value = await peopleStore.fetchActiveSpecialists("assembler") || []
    programmers.value = await peopleStore.fetchActiveSpecialists("programmer") || []
    testers.value = await peopleStore.fetchActiveSpecialists("tester") || []
    console.log('developers:', schemDevelopers.value);
  } catch (error) {
    console.error("Ошибка загрузки специалистов:", error);
  }
  // Загружаем список людей
  try {
    await peopleStore.fetchPeople();
    console.log('People loaded:', people.value.length);
    console.log('isLoading:', isLoading.value);
    console.log('error:', error.value);
  } catch (error) {
    console.error('Failed to load people:', error);
  }

  // Загружаем список заказов
  try {
    await ordersStore.fetchOrderSerials(2); // выбираем только заказы которые "в работе"
    console.log('Orders loaded:', orderSerials.value.length);
  } catch (error) {
    console.error('Failed to load orders:', error);
  }
});

// Функция для поиска заказов
function searchOrder(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredOrders.value = orderSerials.value.filter(order =>
      order.serial.toLowerCase().includes(query)
  );
}

// Функция для обработки выбора заказа
function handleOrderSelect(event: { value: typeOrderSerial }) {
  // Устанавливаем id заказа в новую запись
  newBox.value.order_id = event.value.serial;
  console.log('Selected order:', event.value);
}

// Для выбора разработчика схемы
const selectedShemDeveloper = ref(null);
const filteredShemDevelopers = ref<Person[]>([]);

// Функция для поиска разработчиков
function searchSchemDevelopers(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredShemDevelopers.value = schemDevelopers.value.filter(developer =>
      developer.name.toLowerCase().includes(query)
  );
}

// Функция для обработки выбора разработчика
function handleSchemDeveloperSelect(event: { value: Person }) {
  newBox.value.scheme_developer_id = event.value.uuid;
  console.log('Selected developer:', event.value);
}


// Для выбора сборщика
const selectedAssembler = ref(null);
const filteredAssemblers = ref<Person[]>([]);

// Функция для поиска сборщиков
function searchAssemblers(event: { query: string }) {
  const query = event.query.toLowerCase();
  filteredAssemblers.value = assemblers.value.filter(assembler =>
      assembler.name.toLowerCase().includes(query)
  );
}

// Функция для обработки выбора сборщика
function handleAssemblerSelect(event: { value: Person }) {
  newBox.value.assembler_id = event.value.uuid;
  console.log('Selected assembler:', event.value);
}

// Форматирование отображаемого имени
function formatPersonName(person: Person): string {
  if (!person) return '';
  const s = person.surname;
  const n = person.name?.[0] || '';
  const o = person.patronymic?.[0] || '';
  return `${s} ${n}.${o}.`;
}
</script>

<template>
  <!-- Форма для добавления новой записи -->
  <div class="w-full bg-gray-700 p-4 rounded-lg mb-4">
    <h2 class="text-xl font-bold mb-4">Добавление новой записи</h2>

    <!-- Показываем данные -->
    <div v-if="!isLoading " class="w-full">
      <div class="overflow-x-auto">
        <table class="min-w-full bg-gray-700 rounded-lg mb-4 table-fixed">
          <colgroup>
            <col style="width: 6%">  <!-- С/Н -->
            <col style="width: 15%"> <!-- Название -->
            <col style="width: 15%"> <!-- Заказ -->
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

            <!-- Поле для серийного номера (только для чтения) -->
            <td class="px-4 py-2">
              <div class="bg-gray-600 px-2 py-1 rounded">
                <p> {{ nextSerialNum }}</p>
              </div>
            </td>

            <!-- Поле для названия шкафа -->
            <td class="px-4 py-2">
              <input
                  type="text"
                  v-model="newBox.name"
                  class="w-full bg-gray-600 px-2 py-1 rounded"
                  placeholder="Введите название"
              />
            </td>

            <!-- Поле выбора заказа -->
            <td>
              <AutoComplete
                  v-model="selectedOrder"
                  dropdown
                  :suggestions="filteredOrders"
                  :forceSelection="true"
                  @complete="searchOrder($event)"
                  optionLabel="serial"
                  @item-select="handleOrderSelect"
                  size="small"
              />
            </td>

            <!-- Поле выбора разработчика схемы -->
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
                  {{ slotProps.option.surname }} {{ slotProps.option.name[0] }}.{{ slotProps.option.patronymic[0] }}.
                </template>
              </AutoComplete>
            </td>


            <!-- Поле выбора сборщика -->
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
                  {{ slotProps.option.surname }} {{ slotProps.option.name[0] }}.{{ slotProps.option.patronymic[0] }}.
                </template>
              </AutoComplete>
            </td>

            <td class="px-4 py-2">{{ }}</td>
            <td class="px-4 py-2">{{ '' }}</td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Контейнер для кнопок -->
      <div class="flex justify-end space-x-2">
        <!-- Кнопка "Отмена" -->
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

        <!-- Кнопка "Записать" -->
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