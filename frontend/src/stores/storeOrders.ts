// src/stores/storeOrders.ts
import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, computed } from 'vue';
import {typeOrderSerial} from "../types/typeOrder";
import { getApiUrl } from '../utils/apiUrlHelper';


export const useOrdersStore = defineStore('orders', () => {
    // Состояние (state) с использованием ref для реактивности
    const orderSerials = ref<typeOrderSerial[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Действие (action) для получения серийных номеров заказов
    const fetchOrderSerials = async (statusId: number | null = null) => {
        loading.value = true;
        error.value = null;

        try {
            // Формируем параметры запроса
            const params: Record<string, any> = {};
            if (statusId !== null) {
                params.status_id = statusId;
            }

            // Выполняем запрос к API
            const response = await axios.get<typeOrderSerial[]>(`${getApiUrl()}order/read-serial`, { params });

            // Обновляем состояние с полученными данными
            orderSerials.value = response.data;
        } catch (err) {
            console.error('Error fetching order serials:', err);
            // Типизированная обработка ошибки
            if (axios.isAxiosError(err)) {
                error.value = err.response?.data?.detail || err.message || 'Failed to fetch order serials';
            } else {
                error.value = 'Unknown error occurred';
            }
        } finally {
            loading.value = false;
        }
    };

    // Действие для очистки состояния
    const resetOrderSerials = () => {
        orderSerials.value = [];
        error.value = null;
    };

    // Вычисляемые свойства (computed)
    const serialsCount = computed(() => orderSerials.value.length);
    const isLoading = computed(() => loading.value);
    const getError = computed(() => error.value);

    // Возвращаем все, что должно быть доступно из хранилища
    return {
        // Состояние
        orderSerials,
        loading,
        error,

        // Действия
        fetchOrderSerials,
        resetOrderSerials,

        // Вычисляемые свойства
        serialsCount,
        isLoading,
        getError
    };
});