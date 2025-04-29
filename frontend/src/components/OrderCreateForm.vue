<!-- OrderCreateForm.vue -->
<!--suppress VueUnrecognizedSlot -->
<script setup lang="ts">
import {onMounted} from 'vue';
import {reactive, computed} from 'vue';
import {useOrdersStore} from '@/stores/storeOrders';
import {useCounterpartyStore} from '@/stores/storeCounterparty'; // Импортируем store контрагентов
import {useToast} from 'primevue/usetoast';
import BaseModal from '@/components/BaseModal.vue';
import { useWorksStore } from "@/stores/storeWorks";

// PrimeVue компоненты
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';
import Select from 'primevue/select'; // Импортируем компонент выпадающего списка
import ProgressSpinner from 'primevue/progressspinner'; // Для отображения загрузки
import DatePicker from 'primevue/datepicker';
import MultiSelect from 'primevue/multiselect';




const emit = defineEmits(['cancel', 'success']);

// Store и утилиты
const ordersStore = useOrdersStore();
const counterpartyStore = useCounterpartyStore(); // Добавляем store контрагентов
const toast = useToast();
const worksStore = useWorksStore()

// Опции для мультиселекта работ
const workOptions = computed(() => {
  return worksStore.activeWorks.map(work => ({
    name: work.name,
    value: work.id,
    description: work.description || ''
  }));
});

// Состояние формы
const formData = reactive({
  name: '',
  serial: '', // серийный номер нового заказа
  customer_id: null as number | null, // Изменили на null для корректной валидации
  status_id: 1,
  deadline_moment: null as Date | null,
  priority: null as number | null,
  works: [] as number[], // массив ID выбранных работ
});

// Состояние валидации
const errors = reactive({
  name: '',
  customer_id: '',
});

const statusOptions = [
  {value: 1, label: 'Не определён'},
  {value: 2, label: 'На согласовании'},
  {value: 3, label: 'В работе'},
  {value: 4, label: 'Просрочено'},
  {value: 5, label: 'Выполнено в срок'},
  {value: 6, label: 'Выполнено НЕ в срок'},
  {value: 7, label: 'Не согласовано'},
  {value: 8, label: 'На паузе'},
];

// Функция для выбора цвета текста (как в таблице)
function getStatusColor(statusId: number) {
  if (statusId === 1) return '#FACC15'; // text-yellow-400
  if (statusId === 2) return '#60A5FA'; // text-blue-400
  if (statusId === 3) return '#34D399'; // text-green-400
  if (statusId === 4) return '#F87171'; // text-red-400
  if (statusId === 8) return '#FFFFFF'; // допустим, сиреневый text-purple-500
  return '#64748B'; // text-gray-500
}

// Состояние загрузки
const loading = computed(() => ordersStore.isLoading);
const loadingCounterparties = computed(() => counterpartyStore.isLoading);

// Валидация формы
const validateForm = (): boolean => {
  let isValid = true;

  // Валидация названия заказа
  if (!formData.name.trim()) {
    errors.name = 'Название заказа обязательно';
    isValid = false;
  } else {
    errors.name = '';
  }

  // Валидация выбора контрагента
  if (formData.customer_id === null) {
    errors.customer_id = 'Выбор заказчика обязателен';
    isValid = false;
  } else {
    errors.customer_id = '';
  }

  return isValid;
};


const priorityOptions = [
  {label: 'Нет', value: null},
  ...Array.from({length: 10}, (_, i) => ({
    label: (i + 1).toString(),
    value: i + 1,
  }))
];


const today = computed(() => {
  const now = new Date();
  now.setHours(0, 0, 0, 0); // обнуляем часы, чтобы день был текущий, а не по времени
  return now;
});


// Отправка формы
const submitForm = async () => {
  if (!validateForm()) {
    toast.add({severity: 'error', summary: 'Ошибка валидации', detail: 'Пожалуйста, проверьте форму', life: 3000});
    return;
  }

  try {
    // Используем безопасное приведение типа, так как валидация уже подтвердила наличие значения
    const customerId = formData.customer_id as number;

// Преобразование Date в строку ISO
    const deadlineMomentStr = formData.deadline_moment ?
        formData.deadline_moment.toISOString() : null;

    const createdOrder = await ordersStore.createOrder({
      name: formData.name,
      customer_id: customerId,
      status_id: formData.status_id,
      deadline_moment: deadlineMomentStr, // Передаем дедлайн
      priority: formData.priority,
      work_ids: formData.works // выбранные работы
    });

    // Получаем имя контрагента для отображения в сообщении
    const customer = counterpartyStore.getCounterpartyById(customerId);
    const customerName = customer ? counterpartyStore.getFullName(customer) : 'выбранный заказчик';

    toast.add({
      severity: 'success',
      summary: 'Заказ создан',
      detail: `Заказ "${createdOrder.name}" для ${customerName} успешно создан`,
      life: 4000
    });

    // Сбрасываем форму
    formData.name = '';
    formData.customer_id = null;
    errors.name = '';
    errors.customer_id = '';
    formData.priority = null;
    formData.works = [];

    emit('success', createdOrder); // Оповещаем родителя об успехе

  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: ordersStore.error || 'Не удалось создать заказ',
      life: 5000
    });
  }
};

// --- Обработчик нажатия кнопки "Отмена" ---
const handleCancelClick = () => {
  errors.name = '';
  errors.customer_id = '';
  emit('cancel');
};

// Запрос данных при монтировании компонента
onMounted(async () => {
  try {
    // Сначала получаем серийный номер
    formData.serial = await ordersStore.fetchNewOrderSerial();

    // Затем получаем список контрагентов
    await counterpartyStore.fetchCounterparties();

    // Затем получаем список работ
    await worksStore.fetchWorks()

  } catch (error) {
    console.error('Failed to load initial data', error);
    toast.add({
      severity: 'error',
      summary: 'Ошибка загрузки',
      detail: 'Не удалось загрузить необходимые данные',
      life: 5000
    });
  }
});

// Опции для выпадающего списка контрагентов
const customerOptions = computed(() => {
  return counterpartyStore.sortedCounterparties.map(cp => ({
    name: counterpartyStore.getFullName(cp),
    value: cp.id,
    code: cp.id.toString() // Добавляем code для совместимости с шаблоном
  }));
});

// Вспомогательная функция для получения имени по ID
const getCustomerNameById = (id: number): string => {
  const customer = counterpartyStore.getCounterpartyById(id);
  return customer ? counterpartyStore.getFullName(customer) : 'Заказчик не найден';
};


</script>

<template>
  <BaseModal
      name="Создание нового заказа"
      :on-close="handleCancelClick"
  >
    <Toast/>

    <form @submit.prevent="submitForm" class="space-y-4">

      <!-- Grid-контейнер для формы -->
      <div class="grid grid-cols-[150px_1fr] gap-4 items-start">

        <!-- Серийный номер -->
        <label for="o-serial" class="text-sm font-medium pt-2">Серийный номер:</label>
        <div>
          <InputText
              id="o-serial"
              v-model="formData.serial"
              class="w-full"
              readonly
              placeholder="Автоматически сгенерированный номер"
          />
        </div>

        <!-- Название заказа -->
        <label for="o-name" class="text-sm font-medium pt-2">Название заказа: <span class="text-red-500">*</span></label>
        <div>
          <InputText
              id="o-name"
              v-model="formData.name"
              class="w-full"
              :class="{ 'p-invalid': errors.name }"
              placeholder="Введите название заказа"
              autocomplete="off"
          />
          <small v-if="errors.name" class="p-error block mt-1">{{ errors.name }}</small>
        </div>

        <!-- Заказчик (контрагент) с поиском -->
        <label for="o-name" class="text-sm font-medium pt-2">Заказчик: <span class="text-red-500">*</span></label>
        <div>
          <div v-if="loadingCounterparties" class="flex items-center">
            <ProgressSpinner style="width: 1.5rem; height: 1.5rem"/>
            <span class="ml-2 text-sm text-gray-500">Загрузка заказчиков...</span>
          </div>

          <Select
              v-else
              id="o-customer"
              v-model="formData.customer_id"
              :options="customerOptions"
              optionValue="value"
              filter
              optionLabel="name"
              placeholder="Выберите заказчика"
              class="w-full"
              :class="{ 'p-invalid': errors.customer_id }"
              :autoFilterFocus="true"
          >
            <!-- Шаблон для отображения выбранного значения -->
            <template #value="slotProps">
              <div v-if="slotProps.value" class="flex items-center">
                <div>
                  {{
                    typeof slotProps.value === 'object' && slotProps.value.name
                        ? slotProps.value.name
                        : getCustomerNameById(slotProps.value)
                  }}
                </div>
              </div>
              <span v-else>
                {{ slotProps.placeholder }}
              </span>
            </template>

            <!-- Шаблон для отображения опций -->
            <template #option="slotProps">
              <div class="flex items-center">
                <div>{{ slotProps.option.name }}</div>
              </div>
            </template>
          </Select>

          <small v-if="errors.customer_id" class="p-error block mt-1">{{ errors.customer_id }}</small>

          <!-- Информация, если нет контрагентов -->
          <small
              v-if="!loadingCounterparties && customerOptions.length === 0"
              class="text-yellow-600 block mt-1"
          >
            Нет доступных заказчиков. Пожалуйста, сначала добавьте контрагентов.
          </small>
        </div>

        <!-- Дедлайн заказа -->
        <label for="o-deadline" class="text-sm font-medium pt-2">Дедлайн:</label>
        <div>
          <DatePicker
              id="o-deadline"
              v-model="formData.deadline_moment"
              class="w-full"
              dateFormat="dd.mm.yy"
              placeholder="Выберите дату дедлайна"
              :showIcon="true"
              :minDate="today"
          />
        </div>

        <!-- Приоритет и статус на одной строке -->
        <label class="text-sm font-medium pt-2">Приоритет и статус:</label>
        <div class="flex flex-row gap-4 items-end">
          <!-- Приоритет -->
          <div class="flex-1 min-w-0">
            <label for="o-priority" class="block text-xs font-medium mb-1">Приоритет</label>
            <Select
                id="o-priority"
                v-model="formData.priority"
                :options="priorityOptions"
                :optionLabel="'label'"
                :optionValue="'value'"
                placeholder="Нет"
                class="w-full"
                :clearable="true"
            >
              <template #option="slotProps">
                <div class="flex items-center">
                  <div :class="`priority-indicator priority-${slotProps.option.value}`"
                       class="w-3 h-3 rounded-full mr-2"></div>
                  <span>{{ slotProps.option.label }}</span>
                </div>
              </template>
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center">
                  <div :class="`priority-indicator priority-${slotProps.value}`"
                       class="w-3 h-3 rounded-full mr-2"></div>
                  <span>{{ priorityOptions.find(opt => opt.value === slotProps.value)?.label || 'Нет' }}</span>
                </div>
                <span v-else>{{ slotProps.placeholder }}</span>
              </template>
            </Select>
          </div>

          <!-- Статус -->
          <div class="flex-1 min-w-0">
            <label for="status" class="block text-xs font-medium mb-1">Статус</label>
            <Select
                id="o-status"
                v-model="formData.status_id"
                :options="statusOptions"
                :optionLabel="'label'"
                :optionValue="'value'"
                placeholder="Выберите статус"
                class="w-full"
            >
              <template #option="slotProps">
                <div class="flex items-center">
                  <span :style="{ color: getStatusColor(slotProps.option.value) }">{{ slotProps.option.label }}</span>
                </div>
              </template>
              <template #value="slotProps">
                <span v-if="slotProps.value" :style="{ color: getStatusColor(slotProps.value) }">
                  {{ statusOptions.find(opt => opt.value === slotProps.value)?.label || 'Не выбрано' }}
                </span>
                <span v-else>{{ slotProps.placeholder }}</span>
              </template>
            </Select>
          </div>


          </div>

        <!-- Выбор работ -->
        <label for="o-works" class="text-sm font-medium pt-2">Работы по заказу:</label>
        <div>
          <div v-if="worksStore.isLoading" class="flex items-center">
            <ProgressSpinner style="width: 1.5rem; height: 1.5rem"/>
            <span class="ml-2 text-sm text-gray-500">Загрузка списка работ...</span>
          </div>

          <MultiSelect
              v-else
              id="o-works"
              v-model="formData.works"
              :options="workOptions"
              optionValue="value"
              optionLabel="name"
              display="chip"
              placeholder="Выберите работы по заказу"
              class="w-full"
              filter
              :maxSelectedLabels="2"
              selectedItemsLabel="{0} работ выбрано"
          >
            <template #option="slotProps">
              <div class="flex align-items-center">
                <div>
                  <div>{{ slotProps.option.name }}</div>
                  <small v-if="slotProps.option.description" class="text-gray-500">
                    {{ slotProps.option.description }}
                  </small>
                </div>
              </div>
            </template>

            <template #emptyfilter>
              <div class="px-3 py-2 text-gray-500">
                Работы не найдены
              </div>
            </template>

            <template #empty>
              <div class="px-3 py-2 text-gray-500">
                Работы не определены в системе
              </div>
            </template>

          </MultiSelect>
        </div>

      </div>

      <!-- Кнопки действий -->
      <div class="flex justify-end gap-2 mt-6">
        <Button
            type="button"
            label="Отмена"
            class="p-button-outlined"
            @click="handleCancelClick"
        />
        <Button
            type="submit"
            label="Создать заказ"
            icon="pi pi-check"
            :loading="loading"
            :disabled="loadingCounterparties || customerOptions.length === 0"
        />
      </div>

    </form>
  </BaseModal>
</template>


<style scoped>

</style>