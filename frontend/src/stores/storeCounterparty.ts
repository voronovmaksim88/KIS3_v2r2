// storeCounterparty.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { Counterparty } from '../types/typeCounterparty';
import { getApiUrl } from '../utils/apiUrlHelper';

export const useCounterpartyStore = defineStore('counterparty', () => {
    // Состояние
    const counterparties = ref<Counterparty[]>([]);
    const error = ref<string>('');
    const isLoading = ref<boolean>(false);

    // Геттеры (computed properties)
    const sortedCounterparties = computed(() => {
        // Добавляем проверку на пустой массив
        if (!counterparties.value || counterparties.value.length === 0) {
            return [];
        }

        return [...counterparties.value].sort((a, b) => {
            // Добавляем защиту от undefined
            const nameA = a.name || '';
            const nameB = b.name || '';
            return nameA.localeCompare(nameB);
        });
    });

    // Методы
    function clearError() {
        error.value = '';
    }

    async function fetchCounterparties() {
        clearError();
        isLoading.value = true;

        try {
            const response = await axios.get<Counterparty[]>(
                `${getApiUrl()}counterparty/read`,
                { withCredentials: true }
            );

            counterparties.value = response.data;
            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error fetching counterparties:', e.response?.data || e.message);
                error.value = e.response?.data?.detail || 'Error fetching counterparties';
            } else {
                console.error('Unexpected error:', e);
                error.value = 'Unknown error occurred';
            }
            return null;
        } finally {
            isLoading.value = false;
        }
    }

    // Получение контрагента по ID
    function getCounterpartyById(id: number): Counterparty | undefined {
        return counterparties.value.find(counterparty => counterparty.id === id);
    }

    // Функция для получения названия контрагента с формой
    function getFullName(counterparty: Counterparty): string {
        if (!counterparty || !counterparty.form) {
            return 'Неизвестный контрагент';
        }
        return `${counterparty.form.name} "${counterparty.name}"`;
    }

    return {
        // Состояние
        counterparties,
        error,
        isLoading,

        // Геттеры
        sortedCounterparties,

        // Методы
        fetchCounterparties,
        getCounterpartyById,
        getFullName
    };
});