// src/stores/storeOrders.ts
import {defineStore} from 'pinia';
// import {storeToRefs} from 'pinia'; // Не используется здесь
import axios from 'axios';
import {ref, computed} from 'vue';
// Импортируем все необходимые типы
import {
    typeOrderSerial,
    typeOrderRead,
    typePaginatedOrderResponse,
    typeFetchOrdersParams,
    typeOrderDetail,
    typeOrderCreate, typeOrderEdit
} from "../types/typeOrder";
import {getApiUrl} from '../utils/apiUrlHelper';
import { useOrdersTableStore } from '@/stores/storeOrdersTable';

export const useOrdersStore = defineStore('orders', () => {
    // === Состояние ===
    const orderSerials = ref<typeOrderSerial[]>([]); // Список только серийных номеров (если нужен)
    const orders = ref<typeOrderRead[]>([]);         // Полные данные заказов для текущей страницы
    const totalOrders = ref<number>(0);             // Общее количество заказов для пагинации
    const currentLimit = ref<number>(50);           // Лимит заказов на странице
    const currentSkip = ref<number>(0);              // Смещение для пагинации
    const currentOrderDetail = ref<typeOrderDetail | null>(null); // Детали выбранного заказа
    const currentSortField = ref<string>('serial');     // Поле сортировки
    const currentSortDirection = ref<string>('asc');    // Направление сортировки
    const newOrderSerial = ref<string>('');             // Сгенерированный серийный номер для нового заказа
    const error = ref<string | null>(null);             // Общая ошибка стора (можно разделить при необходимости)

    // --- Флаги загрузки ---
    const loading = ref(false);                   // Основной флаг загрузки (для fetchOrders, create, update)
    const detailLoading = ref(false);             // Флаг загрузки деталей заказа (fetchOrderDetail)
    const newSerialLoading = ref(false);          // <<< НОВЫЙ ФЛАГ: Загрузка нового серийного номера
    const serialsLoading = ref(false);            // <<< НОВЫЙ ФЛАГ: Загрузка списка серийных номеров (fetchOrderSerials)

    // === Словарь статусов заказов ===
    const orderStatuses = {
        1: "Не определён", 2: "На согласовании", 3: "В работе", 4: "Просрочено",
        5: "Выполнено в срок", 6: "Выполнено НЕ в срок", 7: "Не согласовано", 8: "На паузе"
    };

    // === Хелпер для обработки ошибок Axios ===
    const handleAxiosError = (err: unknown, defaultMessage: string) => {
        if (axios.isAxiosError(err)) {
            error.value = err.response?.data?.detail || err.message || defaultMessage;
        } else if (err instanceof Error) {
            error.value = err.message;
        } else {
            error.value = 'An unknown error occurred';
        }
        console.error(`${defaultMessage}:`, err);
    };

    // === Действия (Actions) ===

    const clearError = () => { error.value = null; };

    const getStatusText = (statusId: number | null): string => {
        if (statusId === null || statusId === undefined) return "Неизвестный статус";
        return orderStatuses[statusId as keyof typeof orderStatuses] || "Неизвестный статус";
    };

    // --- Действия связанные с получением данных ---

    const fetchOrders = async (params: typeFetchOrdersParams = {}) => {
        loading.value = true; // Используем основной флаг
        error.value = null;
        // ... (остальная логика fetchOrders без изменений) ...
        const queryParams: Record<string, any> = {};
        queryParams.skip = params.skip !== undefined ? params.skip : currentSkip.value;
        queryParams.limit = params.limit !== undefined ? params.limit : currentLimit.value;
        if (params.statusId !== undefined && params.statusId !== null) queryParams.status_id = params.statusId;
        if (params.searchSerial !== undefined && params.searchSerial !== null) queryParams.search_serial = params.searchSerial;
        if (params.searchCustomer !== undefined && params.searchCustomer !== null) queryParams.search_customer = params.searchCustomer;
        if (params.searchPriority !== undefined && params.searchPriority !== null) queryParams.search_priority = params.searchPriority;
        if (params.showEnded !== undefined) {
            queryParams.show_ended = params.showEnded;
        } else {
            const ordersTableStore = useOrdersTableStore();
            queryParams.show_ended = ordersTableStore.showEndedOrders;
        }
        if (params.sortField !== undefined) {
            queryParams.sort_field = params.sortField;
        } else {
            queryParams.sort_field = currentSortField.value;
        }
        if (params.sortDirection !== undefined) {
            queryParams.sort_direction = params.sortDirection;
        } else {
            queryParams.sort_direction = currentSortDirection.value;
        }

        try {
            const response = await axios.get<typePaginatedOrderResponse>(`${getApiUrl()}order/read`, {
                params: queryParams,
                withCredentials: true
            });
            orders.value = response.data.data;
            totalOrders.value = response.data.total;
            currentSkip.value = queryParams.skip;
            if (queryParams.limit !== undefined) {
                currentLimit.value = queryParams.limit;
            }
        } catch (err) {
            handleAxiosError(err, 'Failed to fetch orders');
            orders.value = [];
            totalOrders.value = 0;
        } finally {
            loading.value = false; // Сбрасываем основной флаг
        }
    };

    const fetchOrderDetail = async (serial: string) => {
        detailLoading.value = true; // Используем флаг деталей
        error.value = null;
        currentOrderDetail.value = null;
        try {
            const response = await axios.get<typeOrderDetail>(`${getApiUrl()}order/detail/${serial}`, {
                withCredentials: true
            });
            currentOrderDetail.value = response.data;
        } catch (err) {
            handleAxiosError(err, `Failed to fetch order details for ${serial}`);
            currentOrderDetail.value = null;
        } finally {
            detailLoading.value = false; // Сбрасываем флаг деталей
        }
    };

    // Получение нового серийного номера для создания заказа
    const fetchNewOrderSerial = async () => {
        newSerialLoading.value = true; // <<< Устанавливаем НОВЫЙ флаг
        error.value = null;
        newOrderSerial.value = '';

        try {
            const response = await axios.get<typeOrderSerial>(
                `${getApiUrl()}order/new-serial`,
                { withCredentials: true }
            );
            newOrderSerial.value = response.data.serial;
            return response.data.serial;
        } catch (err) {
            handleAxiosError(err, 'Failed to fetch new order serial');
            return '';
        } finally {
            newSerialLoading.value = false; // <<< Сбрасываем НОВЫЙ флаг
        }
    };

    // Получение только серийных номеров (если еще используется)
    const fetchOrderSerials = async (statusId: number | null = null) => {
        serialsLoading.value = true; // <<< Устанавливаем НОВЫЙ флаг
        error.value = null;
        orderSerials.value = []; // Сбрасываем перед запросом

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
            handleAxiosError(err, 'Failed to fetch order serials');
            orderSerials.value = []; // Убедимся, что сброшено при ошибке
        } finally {
            serialsLoading.value = false; // <<< Сбрасываем НОВЫЙ флаг
        }
    };

    // --- Действия связанные с изменением данных (CRUD) ---

    const createOrder = async (orderData: typeOrderCreate): Promise<typeOrderRead | null> => {
        loading.value = true; // Используем основной флаг
        error.value = null;
        try {
            const response = await axios.post<typeOrderRead>(
                `${getApiUrl()}order/create`, orderData, { withCredentials: true }
            );
            await fetchOrders({ skip: 0, limit: currentLimit.value });
            return response.data;
        } catch (err) {
            handleAxiosError(err, 'Failed to create order');
            throw err;
        } finally {
            loading.value = false; // Сбрасываем основной флаг
        }
    };

    const updateOrder = async (serial: string, orderData: typeOrderEdit): Promise<typeOrderRead | null> => {
        loading.value = true; // Используем основной флаг
        error.value = null;
        try {
            const response = await axios.patch<typeOrderRead>(
                `${getApiUrl()}order/edit/${serial}`, { order_data: orderData }, { withCredentials: true }
            );
            await fetchOrders({ skip: currentSkip.value, limit: currentLimit.value });
            if (currentOrderDetail.value?.serial === serial) {
                // Обновляем детали из ответа или перезапрашиваем
                currentOrderDetail.value = { ...currentOrderDetail.value, ...response.data };
                // await fetchOrderDetail(serial); // Альтернатива
            }
            return response.data;
        } catch (err) {
            handleAxiosError(err, `Failed to update order ${serial}`);
            throw err;
        } finally {
            loading.value = false; // Сбрасываем основной флаг
        }
    };


    // --- Действия связанные с состоянием UI (Сортировка, Сброс) ---

    const setSortField = async (field: string) => {
        const newDirection = (currentSortField.value === field && currentSortDirection.value === 'asc') ? 'desc' : 'asc';
        currentSortField.value = field;
        currentSortDirection.value = newDirection;
        try {
            // fetchOrders сам установит loading = true/false
            await fetchOrders({
                skip: 0,
                limit: currentLimit.value,
                sortField: currentSortField.value,
                sortDirection: currentSortDirection.value,
            });
        } catch (err) {
            console.error('Error occurred while applying sorting:', err);
        }
    };

    const resetSorting = () => {
        currentSortField.value = 'serial';
        currentSortDirection.value = 'asc';
    };

    const resetOrderDetail = () => {
        currentOrderDetail.value = null;
        detailLoading.value = false;
    };

    const resetOrders = () => {
        orders.value = [];
        totalOrders.value = 0;
        currentLimit.value = 50;
        currentSkip.value = 0;
        resetSorting();
    };

    const resetOrderSerials = () => {
        orderSerials.value = [];
        serialsLoading.value = false; // Сбрасываем и флаг загрузки
    };


    // === Вычисляемые свойства (Computed/Getters) ===
    const isLoading = computed(() => loading.value); // Основная загрузка
    const isDetailLoading = computed(() => detailLoading.value); // Загрузка деталей
    const isNewSerialLoading = computed(() => newSerialLoading.value); // <<< НОВОЕ: Загрузка нового номера
    const isSerialsLoading = computed(() => serialsLoading.value); // <<< НОВОЕ: Загрузка списка номеров
    const hasOrderDetail = computed(() => currentOrderDetail.value !== null);
    const currentPage = computed(() => currentLimit.value > 0 ? Math.floor(currentSkip.value / currentLimit.value) : 0);
    const totalPages = computed(() => currentLimit.value > 0 ? Math.ceil(totalOrders.value / currentLimit.value) : 0);
    const serialsCount = computed(() => orderSerials.value.length); // Если используется

    // === Возвращаем все элементы стора ===
    return {
        // Состояния (State)
        orders, totalOrders, currentLimit, currentSkip, currentOrderDetail,
        currentSortField, currentSortDirection, newOrderSerial, orderSerials,
        error,
        // --- Флаги загрузки ---
        loading,          // Основной
        detailLoading,    // Детали
        newSerialLoading, // <<< НОВЫЙ ФЛАГ СОСТОЯНИЯ
        serialsLoading,   // <<< НОВЫЙ ФЛАГ СОСТОЯНИЯ

        // Действия (Actions)
        fetchOrders, fetchOrderDetail, fetchNewOrderSerial, fetchOrderSerials,
        createOrder, updateOrder, setSortField, clearError, getStatusText,
        resetOrders, resetOrderDetail, resetOrderSerials, resetSorting,

        // Вычисляемые свойства (Getters/Computed)
        isLoading,          // Основной
        isDetailLoading,    // Детали
        isNewSerialLoading, // <<< НОВОЕ COMPUTED СВОЙСТВО
        isSerialsLoading,   // <<< НОВОЕ COMPUTED СВОЙСТВО
        hasOrderDetail, currentPage, totalPages, serialsCount,
    };
});
