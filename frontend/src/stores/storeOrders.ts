// src/stores/storeOrders.ts
import {defineStore} from 'pinia';
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


export const useOrdersStore = defineStore('orders', () => {
    // === Существующее состояние ===
    const orderSerials = ref<typeOrderSerial[]>([]);
    const loading = ref(false); // Общий индикатор загрузки для простоты
    const error = ref<string | null>(null);

    // === Новое состояние для полного списка заказов и пагинации ===
    const orders = ref<typeOrderRead[]>([]); // Список заказов текущей страницы
    const totalOrders = ref<number>(0); // Общее количество заказов (для пагинации)
    const currentLimit = ref<number>(50); // Текущий лимит (сколько на странице)
    const currentSkip = ref<number>(0); // Текущий пропуск (сколько пропущено)

    // === Новое состояние для детальной информации о заказе ===
    const currentOrderDetail = ref<typeOrderDetail | null>(null);
    const detailLoading = ref(false); // Отдельный индикатор загрузки для деталей заказа

    //  === Показывать завершённые заказы ===
    const showEndedOrders = ref<boolean>(false);

    // === Состояние для сортировки ===
    const currentSortField = ref<string>('serial'); // По умолчанию сортировка по серийному номеру
    const currentSortDirection = ref<string>('asc'); // По умолчанию сортировка по возрастанию


    // === Словарь статусов заказов ===
    const orderStatuses = {
        1: "Не определён",
        2: "На согласовании",
        3: "В работе",
        4: "Просрочено",
        5: "Выполнено в срок",
        6: "Выполнено НЕ в срок",
        7: "Не согласовано",
        8: "На паузе"
    };

    // === Функция для преобразования ID статуса в текст ===
    const getStatusText = (statusId: number | null): string => {
        if (statusId === null || statusId === undefined) {
            return "Неизвестный статус";
        }

        return orderStatuses[statusId as keyof typeof orderStatuses] || "Неизвестный статус";
    };

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

    // === Действие для получения заказов с пагинацией, обновленное с параметром showEnded ===
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

        // Добавляем параметр showEnded, только если он явно определен
        if (params.showEnded !== undefined) queryParams.show_ended = params.showEnded;

        // Добавляем параметры сортировки
        if (params.sortField !== undefined) {
            queryParams.sort_field = params.sortField;
            currentSortField.value = params.sortField;
        } else {
            queryParams.sort_field = currentSortField.value;
        }

        if (params.sortDirection !== undefined) {
            queryParams.sort_direction = params.sortDirection;
            currentSortDirection.value = params.sortDirection;
        } else {
            queryParams.sort_direction = currentSortDirection.value;
        }

        try {
            const response = await axios.get<typePaginatedOrderResponse>(`${getApiUrl()}order/read`, {
                params: queryParams, // Используем отфильтрованные параметры
                withCredentials: true
            });

            // Обновляем состояние данными из ответа
            orders.value = response.data.data;
            totalOrders.value = response.data.total;
            currentSkip.value = response.data.skip;

        } catch (err) {
            console.error('Error fetching orders:', err);
            // Сбрасываем данные в случае ошибки, чтобы не показывать старые/неактуальные
            orders.value = [];
            totalOrders.value = 0;
            handleAxiosError(err, 'Failed to fetch orders'); // Используем хелпер
        } finally {
            loading.value = false;
        }
    };

    // === Новое действие для получения детальной информации о заказе ===
    const fetchOrderDetail = async (serial: string) => {
        detailLoading.value = true;
        error.value = null; // Сброс ошибки перед запросом

        try {
            const response = await axios.get<typeOrderDetail>(`${getApiUrl()}order/detail/${serial}`, {
                withCredentials: true
            });

            // Обновляем состояние с полученными данными
            currentOrderDetail.value = response.data;
        } catch (err) {
            console.error('Error fetching order details:', err);
            currentOrderDetail.value = null; // Сбрасываем данные в случае ошибки
            handleAxiosError(err, 'Failed to fetch order details');
        } finally {
            detailLoading.value = false;
        }
    };

    // === Действие для сброса детальной информации о заказе ===
    const resetOrderDetail = () => {
        currentOrderDetail.value = null;
    };

    // === Действие для сброса состояния заказов ===
    const resetOrders = () => {
        orders.value = [];
        totalOrders.value = 0;
        currentLimit.value = 50; // Возвращаем к дефолту
        currentSkip.value = 0;  // Возвращаем к дефолту
        resetSorting(); // Сбрасываем сортировку к дефолтным значениям
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


    // === Действия для управления сортировкой ===
    const setSortField = async (field: string) => {
        // Если поле изменилось - обновляем, если то же самое - инвертируем направление
        if (currentSortField.value !== field) {
            currentSortField.value = field;
            currentSortDirection.value = 'asc'; // По умолчанию при смене поля - сортировка по возрастанию
        } else {
            // Инвертируем направление сортировки
            currentSortDirection.value = currentSortDirection.value === 'asc' ? 'desc' : 'asc';
        }

        // Перезагружаем данные с новыми параметрами сортировки,
        // СОХРАНЯЯ текущие параметры пагинации
        try {
            await fetchOrders({
                skip: currentSkip.value,
                limit: currentLimit.value,
                sortField: currentSortField.value,
                sortDirection: currentSortDirection.value,
                // Добавляем флаг showEnded из компонента
                showEnded: showEndedOrders.value
            });
        } catch (err) {
            console.error('Error when applying sorting:', err);
        }
    };

    const resetSorting = () => {
        currentSortField.value = 'serial';
        currentSortDirection.value = 'asc';
    };


    // === Вычисляемые свойства ===
    const serialsCount = computed(() => orderSerials.value.length);
    const isLoading = computed(() => loading.value);
    const isDetailLoading = computed(() => detailLoading.value);
    const hasOrderDetail = computed(() => currentOrderDetail.value !== null);

    // Вычисляемые свойства для пагинации
    const currentPage = computed(() => {
        // Рассчитываем номер текущей страницы (0-based)
        return currentLimit.value > 0 ? Math.floor(currentSkip.value / currentLimit.value) : 0;
    });
    const totalPages = computed(() => {
        // Рассчитываем общее количество страниц
        return currentLimit.value > 0 ? Math.ceil(totalOrders.value / currentLimit.value) : 0;
    });


    // Добавьте эту функцию в store после других функций
    const createOrder = async (orderData: typeOrderCreate) => {
        loading.value = true;
        error.value = null;

        try {
            const response = await axios.post<typeOrderRead>(
                `${getApiUrl()}order/create`,
                orderData,
                {withCredentials: true}
            );

            // Обновляем список заказов после успешного создания
            await fetchOrders();

            // Возвращаем созданный заказ
            return response.data;
        } catch (err) {
            console.error('Error creating order:', err);
            handleAxiosError(err, 'Failed to create order');
            throw err; // Пробрасываем ошибку дальше для обработки в компоненте
        } finally {
            loading.value = false;
        }
    };

    const newOrderSerial = ref<string>('');

    // Добавить новую функцию после других функций
    const fetchNewOrderSerial = async () => {
        loading.value = true;
        error.value = null;

        try {
            const response = await axios.get<typeOrderSerial>(
                `${getApiUrl()}order/new-serial`,
                {withCredentials: true}
            );

            newOrderSerial.value = response.data.serial;
            return response.data.serial;
        } catch (err) {
            console.error('Error fetching new order serial:', err);
            handleAxiosError(err, 'Failed to fetch new order serial');
            return '';
        } finally {
            loading.value = false;
        }
    };


    // Функция для редактирования существующего заказа
    const updateOrder = async (serial: string, orderData: typeOrderEdit) => {
        loading.value = true;
        error.value = null;

        try {
            const response = await axios.patch<typeOrderRead>(
                `${getApiUrl()}order/edit/${serial}`,
                { order_data: orderData }, // Оборачиваем в order_data, как требует API
                { withCredentials: true }
            );

            // Если успешно отредактировали и просматриваем детали этого заказа,
            // обновляем детальную информацию
            if (currentOrderDetail.value?.serial === serial) {
                await fetchOrderDetail(serial);
            }

            // Обновляем список заказов, чтобы отразить изменения
            await fetchOrders({
                skip: currentSkip.value,
                limit: currentLimit.value,
                sortField: currentSortField.value,
                sortDirection: currentSortDirection.value,
                showEnded: showEndedOrders.value
            });

            // Возвращаем обновленный заказ
            return response.data;
        } catch (err) {
            console.error('Error updating order:', err);
            handleAxiosError(err, 'Failed to update order');
            throw err; // Пробрасываем ошибку дальше для обработки в компоненте
        } finally {
            loading.value = false;
        }
    };


    // === Возвращаем все элементы стора ===
    return {
        // Состояния
        orderSerials,
        orders,
        loading,
        error,
        totalOrders,
        currentLimit,
        currentSkip,
        currentOrderDetail, // Состояние для детальной информации
        detailLoading,      // Индикатор загрузки для деталей
        newOrderSerial,        // Состояние для нового серийного номера
        currentSortField,
        currentSortDirection,
        showEndedOrders,

        // Действия
        fetchOrderSerials,
        resetOrderSerials,
        fetchOrders,
        resetOrders,
        clearError,
        getStatusText,
        fetchOrderDetail,  // Действие для получения деталей заказа
        resetOrderDetail,  // Действие для сброса деталей заказа
        createOrder, // Действие для создания заказа
        fetchNewOrderSerial, // Действие для получения нового номера заказа
        setSortField,
        resetSorting,
        updateOrder,

        // Вычисляемые свойства
        serialsCount,
        isLoading,
        isDetailLoading,   // Свойство для проверки загрузки деталей
        hasOrderDetail,    // Свойство для проверки наличия деталей
        currentPage,
        totalPages,
    };
});