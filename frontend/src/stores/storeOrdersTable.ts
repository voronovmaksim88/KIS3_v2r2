// src/stores/storeOrdersTable.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useOrdersTableStore = defineStore('ordersTable', () => {
    // Состояние для отображения завершенных заказов
    const showEndedOrders = ref(false); // По умолчанию скрываем завершённые заказы

    // Действие для переключения состояния
    function toggleShowEndedOrders() {
        showEndedOrders.value = !showEndedOrders.value;
    }

    return {
        showEndedOrders,
        toggleShowEndedOrders,
    };
});