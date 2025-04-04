// src/stores/storeOrders.ts
import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, computed } from 'vue';
// Импортируем все необходимые типы
import {
    typeOrderSerial,
    typeOrderRead,
    typePaginatedOrderResponse,
    typeFetchOrdersParams
} from "../types/typeOrder"; // Убедитесь, что путь к файлу типов верный
import { getApiUrl } from '../utils/apiUrlHelper';


export const useOrdersStore = defineStore('orders', () => {
    // === Существующее состояние ===
    const orderSerials = ref<typeOrderSerial[]>([]);
    const loading = ref(false); // Общий индикатор загрузки для простоты
    const error = ref<string | null>(null);

    // === Новое состояние для полного списка заказов и пагинации ===
    const orders = ref<typeOrderRead[]>([]); // Список заказов текущей страницы
    const totalOrders = ref<number>(0); // Общее количество заказов (для пагинации)
    const currentLimit = ref<number>(10); // Текущий лимит (сколько на странице)
    const currentSkip = ref<number>(0); // Текущий пропуск (сколько пропущено)

    // === Существующие действия ===
    const fetchOrderSerials = async (statusId: number | null = null) => {
        loading.value = true;
        error.value = null;
        try {
            const params: Record<string, any> = {};
            if (statusId !== null) {
                params.status_id = statusId;
            }
            const response = await axios.get<typeOrderSerial[]>(`${getApiUrl()}order/read-serial`, {
                params,
                withCredentials: true
            });
            orderSerials.value = response.data;
        } catch (err) {
            console.error('Error fetching order serials:', err);
            handleAxiosError(err, 'Failed to fetch order serials'); // Используем хелпер для обработки ошибок
        } finally {
            loading.value = false;
        }
    };

    const resetOrderSerials = () => {
        orderSerials.value = [];
        // error.value = null; // Ошибку лучше сбрасывать через clearError или перед новым запросом
    };

    const clearError = () => {
        error.value = null;
    };

    // === Новое действие для получения заказов с пагинацией ===
    const fetchOrders = async (params: typeFetchOrdersParams = {}) => {
        loading.value = true;
        error.value = null; // Сброс ошибки перед запросом

        // Формируем параметры запроса, исключая null/undefined
        const queryParams: Record<string, any> = {};
        if (params.skip !== undefined) queryParams.skip = params.skip;
        if (params.limit !== undefined) queryParams.limit = params.limit;
        if (params.statusId !== undefined && params.statusId !== null) queryParams.status_id = params.statusId;
        if (params.searchSerial !== undefined && params.searchSerial !== null) queryParams.search_serial = params.searchSerial;
        if (params.searchCustomer !== undefined && params.searchCustomer !== null) queryParams.search_customer = params.searchCustomer;
        if (params.searchPriority !== undefined && params.searchPriority !== null) queryParams.search_priority = params.searchPriority;


        try {
            const response = await axios.get<typePaginatedOrderResponse>(`${getApiUrl()}order/read`, {
                params: queryParams, // Используем отфильтрованные параметры
                withCredentials: true
            });

            // Обновляем состояние данными из ответа
            orders.value = response.data.data;
            totalOrders.value = response.data.total;
            currentLimit.value = response.data.limit;
            currentSkip.value = response.data.skip;

        } catch (err) {
            console.error('Error fetching orders:', err);
            // Сбрасываем данные в случае ошибки, чтобы не показывать старые/неактуальные
            orders.value = [];
            totalOrders.value = 0;
            // currentLimit и currentSkip можно оставить или сбросить на дефолт
            handleAxiosError(err, 'Failed to fetch orders'); // Используем хелпер
        } finally {
            loading.value = false;
        }
    };

    // === Новое действие для сброса состояния заказов ===
    const resetOrders = () => {
        orders.value = [];
        totalOrders.value = 0;
        currentLimit.value = 10; // Возвращаем к дефолту
        currentSkip.value = 0;  // Возвращаем к дефолту
        // error.value = null; // Ошибку лучше сбрасывать через clearError
    };

    // === Хелпер для обработки ошибок Axios (чтобы не дублировать код) ===
    const handleAxiosError = (err: unknown, defaultMessage: string) => {
        if (axios.isAxiosError(err)) {
            error.value = err.response?.data?.detail || err.message || defaultMessage;
        } else if (err instanceof Error) {
            error.value = err.message;
        } else {
            error.value = 'An unknown error occurred';
        }
    };


    // === Вычисляемые свойства ===
    const serialsCount = computed(() => orderSerials.value.length);
    const isLoading = computed(() => loading.value);

    // Новые вычисляемые свойства для пагинации
    const currentPage = computed(() => {
        // Рассчитываем номер текущей страницы (0-based)
        return currentLimit.value > 0 ? Math.floor(currentSkip.value / currentLimit.value) : 0;
    });
    const totalPages = computed(() => {
        // Рассчитываем общее количество страниц
        return currentLimit.value > 0 ? Math.ceil(totalOrders.value / currentLimit.value) : 0;
    });

    // === Возвращаем все элементы стора ===
    return {
        // Состояние
        orderSerials,
        orders, // Новый список заказов
        loading,
        error,
        totalOrders, // Новое состояние
        currentLimit, // Новое состояние
        currentSkip,  // Новое состояние

        // Действия
        fetchOrderSerials,
        resetOrderSerials,
        fetchOrders, // Новое действие
        resetOrders, // Новое действие
        clearError,

        // Вычисляемые свойства
        serialsCount,
        isLoading,
        currentPage, // Новое свойство
        totalPages,  // Новое свойство
    };
});