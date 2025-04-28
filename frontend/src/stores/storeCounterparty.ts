// storeCounterparty.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { Counterparty, CounterpartyForm } from '../types/typeCounterparty';
import {getApiUrl} from '../utils/apiUrlHelper';

export const useCounterpartyStore = defineStore('counterparty', () => {
    // Состояние
    const counterparties = ref<Counterparty[]>([]);
    const error = ref<string>('');
    const isLoading = ref<boolean>(false);

    // Геттеры (computed properties)
    const sortedCounterparties = computed(() => {
        return [...counterparties.value].sort((a, b) =>
            a.name.localeCompare(b.name)
        );
    });

    // Получить список форм контрагентов (уникальные значения)
    const counterpartyForms = computed(() => {
        const formMap = new Map<number, CounterpartyForm>();

        counterparties.value.forEach(counterparty => {
            if (!formMap.has(counterparty.form.id)) {
                formMap.set(counterparty.form.id, counterparty.form);
            }
        });

        return Array.from(formMap.values());
    });

    // Методы
    function clearStore() {
        counterparties.value = [];
        error.value = '';
        isLoading.value = false;
    }

    function clearError() {
        error.value = '';
    }

    function setError(message: string) {
        error.value = message;
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
                setError(e.response?.data?.detail || 'Error fetching counterparties');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        } finally {
            isLoading.value = false;
        }
    }

    // Функция для фильтрации контрагентов по форме
    function filterByForm(formId: number): Counterparty[] {
        return counterparties.value.filter(counterparty => counterparty.form.id === formId);
    }

    // Функция для поиска контрагентов по названию
    function searchCounterparties(query: string): Counterparty[] {
        if (!query.trim()) return counterparties.value;

        const lowercaseQuery = query.toLowerCase().trim();
        return counterparties.value.filter(counterparty =>
            counterparty.name.toLowerCase().includes(lowercaseQuery)
        );
    }

    // Получение контрагента по ID
    function getCounterpartyById(id: number): Counterparty | undefined {
        return counterparties.value.find(counterparty => counterparty.id === id);
    }

    // Добавление нового контрагента
    async function addCounterparty(name: string, formId: number) {
        clearError();

        // Валидация входных данных
        if (!name.trim()) {
            setError('Counterparty name is required');
            return null;
        }

        try {
            const response = await axios.post(
                '/api/counterparty/create',
                {
                    name: name.trim(),
                    form_id: formId
                },
                { withCredentials: true }
            );

            // Обновляем список контрагентов после успешного добавления
            await fetchCounterparties();

            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error creating counterparty:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error creating counterparty');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        }
    }

    // Обновление существующего контрагента
    async function updateCounterparty(id: number, name: string, formId: number) {
        clearError();

        // Валидация входных данных
        if (!name.trim()) {
            setError('Counterparty name is required');
            return null;
        }

        try {
            const response = await axios.put(
                `${getApiUrl()}counterparty/update/${id}`,
                {
                    name: name.trim(),
                    form_id: formId
                },
                { withCredentials: true }
            );

            // Обновляем конкретного контрагента в списке
            const index = counterparties.value.findIndex(cp => cp.id === id);
            if (index !== -1) {
                counterparties.value[index] = response.data;
            }

            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error updating counterparty:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error updating counterparty');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        }
    }

    // Удаление контрагента
    async function deleteCounterparty(id: number) {
        clearError();

        try {
            await axios.delete(
                `${getApiUrl()}counterparty/delete/${id}`,
                { withCredentials: true }
            );

            // Удаляем контрагента из списка
            counterparties.value = counterparties.value.filter(cp => cp.id !== id);

            return true;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error deleting counterparty:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error deleting counterparty');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return false;
        }
    }

    // Подсчет количества контрагентов
    const counterpartiesCount = computed(() => counterparties.value.length);

    // Функция для получения названия контрагента с формой
    function getFullName(counterparty: Counterparty): string {
        return `${counterparty.form.name} "${counterparty.name}"`;
    }

    return {
        // Состояние
        counterparties,
        error,
        isLoading,

        // Геттеры
        sortedCounterparties,
        counterpartyForms,
        counterpartiesCount,

        // Методы
        clearStore,
        clearError,
        fetchCounterparties,
        filterByForm,
        searchCounterparties,
        getCounterpartyById,
        addCounterparty,
        updateCounterparty,
        deleteCounterparty,
        getFullName
    };
});