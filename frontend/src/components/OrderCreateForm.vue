<!-- OrderCreateForm.vue -->
<!--suppress VueUnrecognizedSlot -->
<script setup lang="ts">
import { onMounted } from 'vue';
import { reactive, computed } from 'vue';
import { useOrdersStore } from '@/stores/storeOrders';
import { useCounterpartyStore } from '@/stores/storeCounterparty'; // Импортируем store контрагентов
import { useToast } from 'primevue/usetoast';
import BaseModal from '@/components/BaseModal.vue';

// PrimeVue компоненты
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';
import Select from 'primevue/select'; // Импортируем компонент выпадающего списка
import ProgressSpinner from 'primevue/progressspinner'; // Для отображения загрузки

const emit = defineEmits(['cancel', 'success']);

// Store и утилиты
const ordersStore = useOrdersStore();
const counterpartyStore = useCounterpartyStore(); // Добавляем store контрагентов
const toast = useToast();

// Состояние формы
const formData = reactive({
  name: '',
  serial: '', // серийный номер нового заказа
  customer_id: null as number | null, // Изменили на null для корректной валидации
  status_id: 1,   // Временное значение, в будущем добавим выбор статуса
});

// Состояние валидации
const errors = reactive({
  name: '',
  customer_id: '',
});

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

// Отправка формы
const submitForm = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'error', summary: 'Ошибка валидации', detail: 'Пожалуйста, проверьте форму', life: 3000 });
    return;
  }

  try {
    // Используем безопасное приведение типа, так как валидация уже подтвердила наличие значения
    const customerId = formData.customer_id as number;

    const createdOrder = await ordersStore.createOrder({
      name: formData.name,
      customer_id: customerId,
      status_id: formData.status_id,
    });

    // Получаем имя контрагента для отображения в сообщении
    const customer = counterpartyStore.getCounterpartyById(customerId);
    const customerName = customer ? counterpartyStore.getFullName(customer) : 'выбранный заказчик';

    toast.add({
      severity: 'success',
      summary: 'Заказ создан',
      detail: `Заказ "${createdOrder.name}" для ${customerName} успешно создан`,
      life: 3000
    });

    // Сбрасываем форму
    formData.name = '';
    formData.customer_id = null;
    errors.name = '';
    errors.customer_id = '';

    emit('success', createdOrder); // Оповещаем родителя об успехе

  } catch (error) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: ordersStore.error || 'Не удалось создать заказ', life: 5000 });
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
    <Toast />
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
        <label for="o-name" class="text-sm font-medium pt-2">Название заказа:*</label>
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
        <label for="o-customer" class="text-sm font-medium pt-2">Заказчик:*</label>
        <div>
          <div v-if="loadingCounterparties" class="flex items-center">
            <ProgressSpinner style="width: 1.5rem; height: 1.5rem" />
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
                <div> {{
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
      </div>

      <!-- Кнопки действий остаются с прежним расположением -->
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