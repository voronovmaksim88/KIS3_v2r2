<script setup lang="ts">
import { reactive, computed } from 'vue';
import { useOrdersStore } from '@/stores/storeOrders';
import { useToast } from 'primevue/usetoast';

// PrimeVue компоненты
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';

// Определяем пропсы и события
const emit = defineEmits(['success', 'cancel']);

// Store и утилиты
const ordersStore = useOrdersStore();
const toast = useToast();

// Состояние формы
const formData = reactive({
  name: '',
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

  // Проверка названия заказа
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
    toast.add({
      severity: 'error',
      summary: 'Ошибка валидации',
      detail: 'Пожалуйста, проверьте форму и исправьте ошибки',
      life: 3000
    });
    return;
  }

  try {
    const createdOrder = await ordersStore.createOrder({
      name: formData.name,
      customer_id: formData.customer_id,
      status_id: formData.status_id,
    });

    toast.add({
      severity: 'success',
      summary: 'Заказ создан',
      detail: `Заказ "${createdOrder.name}" успешно создан`,
      life: 3000
    });

    // Сбрасываем форму
    formData.name = '';

    // Оповещаем родительский компонент об успешном создании
    emit('success', createdOrder);
  } catch (error) {
    // Ошибка уже обработана в store, здесь можно добавить дополнительную логику
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: ordersStore.error || 'Не удалось создать заказ',
      life: 5000
    });
  }
};
</script>

<template>
  <div class="p-2">
    <Toast />

    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">Создание нового заказа</h2>
      <Button
          icon="pi pi-times"
          class="p-button-rounded p-button-text"
          @click="emit('cancel')"
          aria-label="Закрыть"
      />
    </div>

    <form @submit.prevent="submitForm" class="space-y-4">
      <div class="form-field">
        <label for="name" class="block text-sm font-medium mb-1">Название заказа*</label>
        <InputText
            id="name"
            v-model="formData.name"
            class="w-full"
            :class="{ 'p-invalid': errors.name }"
            placeholder="Введите название заказа"
        />
        <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
      </div>

      <div class="form-actions flex justify-end gap-2 mt-6">
        <Button
            type="button"
            label="Отмена"
            class="p-button-outlined"
            @click="emit('cancel')"
        />
        <Button
            type="submit"
            label="Создать заказ"
            icon="pi pi-check"
            :loading="loading"
        />
      </div>
    </form>
  </div>
</template>



<style scoped>
.form-field {
  @apply mb-2;
}
</style>