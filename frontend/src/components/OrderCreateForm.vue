<-- OrderCreateForm.vue -->
<script setup lang="ts">
import { onMounted } from 'vue';
import { reactive, computed } from 'vue'; // Добавили watch
import { useOrdersStore } from '@/stores/storeOrders';
import { useToast } from 'primevue/usetoast';
import BaseModal from '@/components/BaseModal.vue'; // <--- Импортируем BaseModal

// PrimeVue компоненты
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';

const emit = defineEmits(['cancel', 'success']);

// Store и утилиты
const ordersStore = useOrdersStore();
const toast = useToast();

// Состояние формы
const formData = reactive({
  name: '',
  serial: '', // серийный номер нового заказа
  customer_id: 1, // Временное значение, в будущем добавим выбор контрагента
  status_id: 1,   // Временное значение, в будущем добавим выбор статуса
});

// Состояние валидации
const errors = reactive({
  name: '',
});

// Состояние загрузки
const loading = computed(() => ordersStore.isLoading);


// Валидация формы
const validateForm = (): boolean => {
  let isValid = true;
  if (!formData.name.trim()) {
    errors.name = 'Название заказа обязательно';
    isValid = false;
  } else {
    errors.name = '';
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
    const createdOrder = await ordersStore.createOrder({
      name: formData.name,
      customer_id: formData.customer_id,
      status_id: formData.status_id,
    });

    toast.add({ severity: 'success', summary: 'Заказ создан', detail: `Заказ "${createdOrder.name}" успешно создан`, life: 3000 });

    // Сбрасываем форму
    formData.name = '';
    errors.name = ''; // Сбрасываем ошибки

    emit('success', createdOrder); // Оповещаем родителя об успехе

  } catch (error) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: ordersStore.error || 'Не удалось создать заказ', life: 5000 });
  }
};

// --- Обработчик нажатия кнопки "Отмена" ---
const handleCancelClick = () => {
  errors.name = ''; // Опционально: сбросить ошибку при отмене
  emit('cancel');   // <--- Сообщаем родителю об отмене
};

// Запрос серийного номера при монтировании компонента
onMounted(async () => {
  try {
    formData.serial = await ordersStore.fetchNewOrderSerial();
  } catch (error) {
    console.error('Failed to fetch order serial', error);
  }
});
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
        />
      </div>
    </form>
  </BaseModal>

</template>

<style scoped>
</style>
