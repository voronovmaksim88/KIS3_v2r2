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
    const error = ref<string | null>(null); // Состояние для ошибки

    // Действие (action) для получения серийных номеров заказов
    const fetchOrderSerials = async (statusId: number | null = null) => {
        loading.value = true;
        error.value = null; // Сбрасываем ошибку перед каждым запросом

        try {
            // Формируем параметры запроса
            const params: Record<string, any> = {};
            if (statusId !== null) {
                params.status_id = statusId;
            }

            // Выполняем запрос к API
            const response = await axios.get<typeOrderSerial[]>(`${getApiUrl()}order/read-serial`, {
                params,
                withCredentials: true // Добавляем, если требуется аутентификация через cookie
            });

            // Обновляем состояние с полученными данными
            orderSerials.value = response.data;
        } catch (err) {
            console.error('Error fetching order serials:', err);
            // Типизированная обработка ошибки
            if (axios.isAxiosError(err)) {
                // Пытаемся извлечь 'detail' или используем стандартное сообщение
                error.value = err.response?.data?.detail || err.message || 'Failed to fetch order serials';
            } else if (err instanceof Error) {
                error.value = err.message; // Обработка стандартных ошибок JS
            }
            else {
                error.value = 'An unknown error occurred'; // Обработка неизвестных ошибок
            }
        } finally {
            loading.value = false;
        }
    };

    // Действие для очистки состояния (списка серийных номеров и ошибки)
    const resetOrderSerials = () => {
        orderSerials.value = [];
        error.value = null; // Также сбрасываем ошибку при полном сбросе
    };

    // Действие для очистки только ошибки
    const clearError = () => {
        error.value = null;
    };

    // Вычисляемые свойства (computed)
    const serialsCount = computed(() => orderSerials.value.length);
    const isLoading = computed(() => loading.value);


    // Возвращаем все, что должно быть доступно из хранилища
    return {
        // Состояние (можно получить через storeToRefs или напрямую store.error)
        orderSerials,
        loading,
        error,

        // Действия
        fetchOrderSerials,
        resetOrderSerials,
        clearError,

        // Вычисляемые свойства
        serialsCount,
        isLoading,
    };
});