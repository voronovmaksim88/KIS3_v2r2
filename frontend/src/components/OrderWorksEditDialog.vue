
<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useOrdersStore } from '@/stores/storeOrders';
import { useWorksStore } from '@/stores/storeWorks'; // Import works store
import { useToast } from 'primevue/usetoast';
import type { typeWork } from '@/types/typeWork'; // <-- Import the type

// PrimeVue компоненты
import Dialog from 'primevue/dialog';
import MultiSelect from 'primevue/multiselect';
import Button from 'primevue/button';
import Toast from 'primevue/toast'; // <-- Import Toast for use in template

// Определяем пропсы
const props = defineProps<{
  visible: boolean; // Для v-model
  orderId: string | null;
  initialWorkIds: number[]; // Массив ID текущих работ заказа
}>();

// Определяем события, которые компонент может emit'ить
const emit = defineEmits(['update:visible', 'update-works', 'cancel']);

// --- Store и утилиты ---
const ordersStore = useOrdersStore();
const worksStore = useWorksStore(); // Получаем экземпляр works store
const toast = useToast(); // Используем toast здесь

// --- Локальное состояние ---
const selectedWorkIds = ref<number[]>([]); // ID работ, выбранные в MultiSelect
const originalWorkIds = ref<number[]>([]); // Исходные ID для сравнения
const isWorksUpdateLoading = ref(false); // Состояние загрузки для сохранения
const isWorksLoading = computed(() => worksStore.isLoading); // Состояние загрузки списка работ

// --- Инициализация и Watchers ---

// Инициализация локального состояния при изменении initialWorkIds
watch(() => props.initialWorkIds, (newIds) => {
  // Сортируем для консистентного сравнения
  selectedWorkIds.value = [...newIds].sort((a, b) => a - b);
  originalWorkIds.value = [...newIds].sort((a, b) => a - b);
}, { immediate: true, deep: true });

// Сброс состояния при открытии диалога
watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    // Обновляем состояние из пропсов при каждом открытии
    selectedWorkIds.value = [...props.initialWorkIds].sort((a, b) => a - b);
    originalWorkIds.value = [...props.initialWorkIds].sort((a, b) => a - b);
    isWorksUpdateLoading.value = false;
    // Убедимся, что список *активных* работ загружен, если он еще не загружен
    // Важно: worksStore.fetchWorks() загружает только АКТИВНЫЕ работы
    if (worksStore.works.length === 0 && !worksStore.isLoading) {
      worksStore.fetchWorks(); // Загружаем активные работы
    }
  }
});

// --- Computed Properties ---

// Опции для MultiSelect
// ВАЖНО: Используем sortedWorks, который основан на works (только активные работы из fetchWorks).
// Это означает, что в диалоге будут доступны для выбора ТОЛЬКО активные работы.
// Если заказу была ранее присвоена работа, ставшая неактивной, она не будет отображаться
// в списке выбора и может быть удалена при сохранении, если не будет выбрана заново (что невозможно).
const workOptions = computed(() => {
  // Используем sortedWorks (список только активных работ, отсортированных по имени)
  return worksStore.sortedWorks.map((work: typeWork) => ({ // <-- Явно указываем тип work
    name: work.name,
    value: work.id,
    description: work.description || '', // Используем || '' на случай undefined/null
    active: work.active // Свойство active из typeWork
  }));
});

// Проверка, изменился ли список работ для кнопки "Сохранить"
const isSaveDisabled = computed(() => {
  const currentSorted = [...selectedWorkIds.value].sort((a, b) => a - b);
  const originalSorted = [...originalWorkIds.value].sort((a, b) => a - b);
  // Отключаем, если идет загрузка, нет ID заказа, или массивы идентичны
  return isWorksUpdateLoading.value || !props.orderId || JSON.stringify(currentSorted) === JSON.stringify(originalSorted);
});

// --- Методы ---

/**
 * Обработчик сохранения нового списка работ
 */
const handleUpdateOrderWorks = async () => {
  if (!props.orderId || isSaveDisabled.value) {
    return;
  }

  try {
    isWorksUpdateLoading.value = true;

    await ordersStore.updateOrder(props.orderId, {
      work_ids: selectedWorkIds.value // Передаем выбранные ID
    });

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Список работ для заказа #${props.orderId} обновлен`,
      life: 3000,
      group: 'dialog-toast' // Указываем группу для Toast внутри диалога
    });

    emit('update-works');
    emit('update:visible', false);

  } catch (error) {
    console.error('Ошибка при изменении списка работ заказа:', error);
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Не удалось изменить список работ заказа #${props.orderId}`,
      life: 5000,
      group: 'dialog-toast' // Указываем группу для Toast внутри диалога
    });
  } finally {
    isWorksUpdateLoading.value = false;
  }
};

/**
 * Отменяет редактирование и закрывает диалог
 */
const cancelEdit = () => {
  emit('update:visible', false);
  emit('cancel');
};

</script>

<template>
  <Dialog
      :visible="visible"
      @update:visible="(value) => $emit('update:visible', value)"
      modal
      header="Редактирование работ по заказу"
      :style="{ width: '550px' }"
      :closable="true"
      :dismissableMask="true"
      @hide="cancelEdit"
  >
    <template #header>
      <div class="p-dialog-header">
        <span class="text-lg font-bold">Редактирование работ по заказу #{{ orderId }}</span>
      </div>
    </template>



    <Toast position="top-center" group="dialog-toast" />

    <div class="p-4">
      <div class="mb-4">
        <label for="orderWorksEdit" class="block mb-2">Выберите работы (только активные)</label>
        <MultiSelect
            id="orderWorksEdit"
            v-model="selectedWorkIds"
            :options="workOptions"
            optionValue="value"
            optionLabel="name"
            placeholder="Выберите работы из списка"
            display="chip"
            class="w-full"
            filter
            :loading="isWorksLoading"
            :maxSelectedLabels="5"
            selectedItemsLabel="{0} работ выбрано"
            :selectAll="false"
            :showToggleAll="false"
        >
          <template #option="slotProps">
            <div class="flex align-items-center">
              <div>
                <div>{{ slotProps.option.name }}


                </div>
                <small v-if="slotProps.option.description" class="text-gray-500">
                  {{ slotProps.option.description }}
                </small>
              </div>
            </div>
          </template>

          <template #emptyfilter>
            <div class="px-3 py-2 text-gray-500">
              Активные работы не найдены по запросу
            </div>
          </template>

          <template #empty>
            <div class="px-3 py-2 text-gray-500">
              В системе нет активных работ
            </div>
          </template>
        </MultiSelect>
        <small class="text-xs text-gray-400 mt-1 block">
          Примечание: Отображаются и доступны для выбора только активные виды работ.
        </small>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end space-x-2 p-3">
        <Button
            type="button"
            label="Отмена"
            severity="secondary"
            @click="cancelEdit"
            :disabled="isWorksUpdateLoading"
        />
        <Button
            type="button"
            label="Сохранить"
            icon="pi pi-check"
            :loading="isWorksUpdateLoading"
            :disabled="isSaveDisabled || isWorksLoading"
            @click="handleUpdateOrderWorks"
        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>

</style>
