
<script setup lang="ts">
import {computed, ref, watch} from 'vue';
import { useOrdersStore } from '@/stores/storeOrders';
import { useToast } from 'primevue/usetoast';

// PrimeVue компоненты
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

// Определяем пропсы
const props = defineProps<{
  visible: boolean; // Для v-model
  orderId: string | null;
  initialName: string;
}>();

// Определяем события, которые компонент может emit'ить
const emit = defineEmits(['update:visible', 'update-name', 'cancel']);

// Локальное состояние для диалога
const newOrderName = ref('');
const originalOrderName = ref(''); // Храним исходное название для проверки изменений
const isNameUpdateLoading = ref(false);

// Store и утилиты
const ordersStore = useOrdersStore();
const toast = useToast(); // Используем toast здесь для уведомлений об успешном/неуспешном обновлении

// Инициализация локального состояния при изменении initialName или открытии диалога
watch(() => props.initialName, (newName) => {
  newOrderName.value = newName;
  originalOrderName.value = newName;
}, { immediate: true });

watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    // Сброс состояния при открытии
    newOrderName.value = props.initialName;
    originalOrderName.value = props.initialName;
    isNameUpdateLoading.value = false;
  }
});

/**
 * Обработчик сохранения нового названия заказа
 */
const handleUpdateOrderName = async () => {
  if (!props.orderId || newOrderName.value.trim() === '' || newOrderName.value.trim() === originalOrderName.value) {
    // Если нет ID, имя пустое или не изменилось, просто закрываем или ничего не делаем
    if (props.orderId && newOrderName.value.trim() === originalOrderName.value) {
      emit('update:visible', false); // Закрыть, если имя не изменилось
    }
    return;
  }

  try {
    isNameUpdateLoading.value = true;

    // Обновляем название заказа через store
    await ordersStore.updateOrder(props.orderId, {
      name: newOrderName.value.trim()
    });

    // Показываем уведомление об успехе
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Название заказа #${props.orderId} обновлено`,
      life: 3000
    });

    // Оповещаем родителя об успешном обновлении и закрываем диалог
    emit('update-name', { orderId: props.orderId, newName: newOrderName.value.trim() });
    emit('update:visible', false);

  } catch (error) {
    console.error('Ошибка при изменении названия заказа:', error);
    // Показываем уведомление об ошибке
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Не удалось изменить название заказа #${props.orderId}`,
      life: 5000
    });
  } finally {
    isNameUpdateLoading.value = false;
  }
};

/**
 * Отменяет редактирование названия и закрывает диалог
 */
const cancelEdit = () => {
  emit('update:visible', false);
  emit('cancel');
};

// Проверка, изменилось ли название и не пустое ли оно для кнопки "Сохранить"
const isSaveDisabled = computed(() => {
  return newOrderName.value.trim() === '' || newOrderName.value.trim() === originalOrderName.value || isNameUpdateLoading.value;
});

</script>

<template>



  <Dialog
      :visible="visible"
      @update:visible="(value) => $emit('update:visible', value)"
      modal
      header="Изменение названия заказа"
      :style="{ width: '450px' }"
      :closable="true"
      :dismissableMask="true"
  >
    <template #header>
      <div :class="['p-dialog-header']">
        <span class="text-lg font-bold">Изменение названия заказа</span>
      </div>
    </template>

    <div :class="['p-4']">
      <div class="mb-4">
        <label for="orderNameEdit" class="block mb-2">Название заказа</label>
        <InputText
            id="orderNameEdit"
            v-model="newOrderName"
            class="w-full p-2"
            @keyup.enter="!isSaveDisabled && handleUpdateOrderName()"
        />
      </div>
    </div>

    <template #footer>
      <div :class="['flex justify-end space-x-2 p-3']">
        <Button
            @click="cancelEdit"
            label="Cancel"
            severity="secondary"
        >
          Отмена
        </Button>

        <Button
            @click="handleUpdateOrderName"
            label="Сохранить"
            :loading="isNameUpdateLoading"
            :disabled="isSaveDisabled"
            icon="pi pi-check"
            iconPos="right"
        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
/* Стили для диалога могут быть здесь, или оставлены в TheOrders с :deep */
/* Если оставите в TheOrders, убедитесь, что селекторы правильные */
</style>
