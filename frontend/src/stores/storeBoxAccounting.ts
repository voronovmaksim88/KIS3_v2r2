// storeBoxAccounting.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { BoxAccounting, PaginatedBoxAccounting } from '../types/typeBoxAccounting';
import { getApiUrl } from '../utils/apiUrlHelper';

export const useBoxAccountingStore = defineStore('boxAccounting', () => {
    // Состояние
    const boxes = ref<BoxAccounting[]>([]);
    const error = ref('');
    const isLoading = ref(false);
    const pagination = ref({
        total: 0,
        page: 1,
        size: 20,
        pages: 1
    });

    // Геттеры (computed properties)
    const sortedBoxes = computed(() => {
        return [...boxes.value].sort((a, b) =>
            a.serial_num > b.serial_num ? 1 : -1
        );
    });

    // Методы
    function clearStore() {
        boxes.value = [];
        error.value = '';
        isLoading.value = false;
        pagination.value = {
            total: 0,
            page: 1,
            size: 20,
            pages: 1
        };
    }

    function clearError() {
        error.value = '';
    }

    function setError(message: string) {
        error.value = message;
    }

    async function fetchBoxes(page: number = 1, size: number = 20) {
        clearError();
        isLoading.value = true;

        try {
            const response = await axios.get<PaginatedBoxAccounting>(
                `${getApiUrl()}box-accounting/read/`,
                {
                    params: { page, size },
                    withCredentials: true
                }
            );

            boxes.value = response.data.items;
            pagination.value = {
                total: response.data.total,
                page: response.data.page,
                size: response.data.size,
                pages: response.data.pages
            };
            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error fetching boxes:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error fetching boxes');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        } finally {
            isLoading.value = false;
        }
    }

    async function addBox(
        name: string,
        order_id: string,
        scheme_developer_id: string,
        assembler_id: string,
        programmer_id: string | null,
        tester_id: string
    ) {
        clearError();

        if (!name.trim()) {
            setError('Box name cannot be empty');
            return null;
        }

        try {
            const response = await axios.post(
                `${getApiUrl()}/box-accounting/create/`,
                {
                    name: name.trim(),
                    order_id,
                    scheme_developer_id,
                    assembler_id,
                    programmer_id,
                    tester_id
                },
                { withCredentials: true }
            );

            // Обновляем список шкафов после успешного добавления
            await fetchBoxes(pagination.value.page, pagination.value.size);

            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error creating box:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error creating box');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        }
    }

    async function updateBox(
        serial_num: number,
        name: string,
        order_id: string,
        scheme_developer_id: string,
        assembler_id: string,
        programmer_id: string | null,
        tester_id: string
    ) {
        clearError();

        if (!name.trim()) {
            setError('Box name cannot be empty');
            return null;
        }

        try {
            const response = await axios.put(
                `${getApiUrl()}/-/update/${serial_num}`,
                {
                    name: name.trim(),
                    order_id,
                    scheme_developer_id,
                    assembler_id,
                    programmer_id,
                    tester_id
                },
                { withCredentials: true }
            );

            // Обновляем конкретный шкаф в списке
            const index = boxes.value.findIndex(box => box.serial_num === serial_num);
            if (index !== -1) {
                boxes.value[index] = response.data;
            }

            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error updating box:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error updating box');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        }
    }

    async function changePage(page: number) {
        if (page < 1 || page > pagination.value.pages) {
            return false;
        }
        return await fetchBoxes(page, pagination.value.size) !== null;
    }

    async function changePageSize(size: number) {
        return await fetchBoxes(1, size) !== null;
    }

    // Функция для получения шкафа по его серийному номеру
    function getBoxBySerialNum(serial_num: number): BoxAccounting | undefined {
        return boxes.value.find(box => box.serial_num === serial_num);
    }

    return {
        // Состояние
        boxes,
        error,
        isLoading,
        pagination,

        // Геттеры
        sortedBoxes,

        // Методы
        clearStore,
        clearError,
        fetchBoxes,
        addBox,
        updateBox,
        changePage,
        changePageSize,
        getBoxBySerialNum
    };
});