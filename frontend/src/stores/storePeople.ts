// storePeople.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { Person } from '../types/typePerson';
import { getApiUrl } from '../utils/apiUrlHelper';

// Создайте тип для параметров фильтрации
interface PeopleFilterParams {
    can_be_any?: boolean;
    can_be_scheme_developer?: boolean;
    can_be_assembler?: boolean;
    can_be_programmer?: boolean;
    can_be_tester?: boolean;
    active?: boolean;
    counterparty_id?: number;
}

export const usePeopleStore = defineStore('people', () => {
    // Состояние
    const people = ref<Person[]>([]);
    const error = ref('');
    const isLoading = ref(false);

    // Геттеры (computed properties)
    const sortedPeople = computed(() => {
        return [...people.value].sort((a, b) =>
            a.surname > b.surname ? 1 : a.surname === b.surname ?
                (a.name > b.name ? 1 : -1) : -1
        );
    });

    // Полное имя для отображения (Фамилия И. О.)
    const getFormattedName = (person: Person) => {
        return `${person.surname} ${person.name[0]}.${person.patronymic[0]}.`;
    };

    // Методы
    function clearStore() {
        people.value = [];
        error.value = '';
        isLoading.value = false;
    }

    function clearError() {
        error.value = '';
    }

    function setError(message: string) {
        error.value = message;
    }

    async function fetchAllPeople() {
        clearError();
        isLoading.value = true;

        try {
            const response = await axios.get<Person[]>(
                `${getApiUrl()}get_all/people/`,
                { withCredentials: true }
            );

            people.value = response.data;
            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error fetching people:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error fetching people');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        } finally {
            isLoading.value = false;
        }
    }


    async function fetchPeople(filters: PeopleFilterParams = {}) {
        clearError();
        isLoading.value = true;

        try {
            // Создаем параметры запроса на основе предоставленных фильтров
            const params: Record<string, string | number | boolean> = {};

            // Добавляем только определенные (не undefined) фильтры
            if (filters.can_be_any !== undefined) params.can_be_any = filters.can_be_any;
            if (filters.can_be_scheme_developer !== undefined) params.can_be_scheme_developer = filters.can_be_scheme_developer;
            if (filters.can_be_assembler !== undefined) params.can_be_assembler = filters.can_be_assembler;
            if (filters.can_be_programmer !== undefined) params.can_be_programmer = filters.can_be_programmer;
            if (filters.can_be_tester !== undefined) params.can_be_tester = filters.can_be_tester;
            if (filters.active !== undefined) params.active = filters.active;
            if (filters.counterparty_id !== undefined) params.counterparty_id = filters.counterparty_id;

            const response = await axios.get<Person[]>(
                `${getApiUrl()}person/read`,
                {
                    params,
                    withCredentials: true
                }
            );

            people.value = response.data;
            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error fetching people:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error fetching people');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        } finally {
            isLoading.value = false;
        }
    }

    // Удобные предустановленные фильтры для частых сценариев
    async function fetchActivePeople() {
        return fetchPeople({ active: true });
    }

    async function fetchDevelopers() {
        return fetchPeople({ can_be_scheme_developer: true });
    }

    async function fetchAssemblers() {
        return fetchPeople({ can_be_assembler: true });
    }

    async function fetchProgrammers() {
        return fetchPeople({ can_be_programmer: true });
    }

    async function fetchTesters() {
        return fetchPeople({ can_be_tester: true });
    }

    async function fetchAnySpecialists() {
        return fetchPeople({ can_be_any: true });
    }

    // Функция для фильтрации по компании
    async function fetchPeopleByCounterparty(counterpartyId: number) {
        return fetchPeople({ counterparty_id: counterpartyId });
    }

    // Функция для комбинированной фильтрации (по роли и активности)
    async function fetchActiveSpecialists(specialistType: 'developer' | 'assembler' | 'programmer' | 'tester' | 'any') {
        const filters: PeopleFilterParams = { active: true };

        switch (specialistType) {
            case 'developer':
                filters.can_be_scheme_developer = true;
                break;
            case 'assembler':
                filters.can_be_assembler = true;
                break;
            case 'programmer':
                filters.can_be_programmer = true;
                break;
            case 'tester':
                filters.can_be_tester = true;
                break;
            case 'any':
                filters.can_be_any = true;
                break;
        }

        return fetchPeople(filters);
    }


    async function addPerson(
        name: string,
        surname: string,
        patronymic: string
    ) {
        clearError();

        // Валидация входных данных
        if (!name.trim() || !surname.trim() || !patronymic.trim()) {
            setError('All fields are required (name, surname, patronymic)');
            return null;
        }

        try {
            const response = await axios.post(
                `${getApiUrl()}/people/create/`,
                {
                    name: name.trim(),
                    surname: surname.trim(),
                    patronymic: patronymic.trim()
                },
                { withCredentials: true }
            );

            // Обновляем список людей после успешного добавления
            await fetchAllPeople();

            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error creating person:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error creating person');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        }
    }

    async function updatePerson(
        uuid: string,
        name: string,
        surname: string,
        patronymic: string
    ) {
        clearError();

        // Валидация входных данных
        if (!name.trim() || !surname.trim() || !patronymic.trim()) {
            setError('All fields are required (name, surname, patronymic)');
            return null;
        }

        try {
            const response = await axios.put(
                `${getApiUrl()}/people/update/${uuid}`,
                {
                    name: name.trim(),
                    surname: surname.trim(),
                    patronymic: patronymic.trim()
                },
                { withCredentials: true }
            );

            // Обновляем конкретного человека в списке
            const index = people.value.findIndex(person => person.uuid === uuid);
            if (index !== -1) {
                people.value[index] = response.data;
            }

            return response.data;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error updating person:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error updating person');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return null;
        }
    }

    async function deletePerson(apiUrl: string, uuid: string) {
        clearError();

        try {
            await axios.delete(
                `${apiUrl}/people/delete/${uuid}`,
                { withCredentials: true }
            );

            // Удаляем человека из списка
            people.value = people.value.filter(person => person.uuid !== uuid);

            return true;
        } catch (e) {
            if (axios.isAxiosError(e)) {
                console.error('Error deleting person:', e.response?.data || e.message);
                setError(e.response?.data?.detail || 'Error deleting person');
            } else {
                console.error('Unexpected error:', e);
                setError('Unknown error occurred');
            }
            return false;
        }
    }

    // Функция для получения человека по uuid
    function getPersonByUuid(uuid: string): Person | undefined {
        return people.value.find(person => person.uuid === uuid);
    }

    // Функция для поиска людей
    function searchPeople(query: string): Person[] {
        if (!query.trim()) return people.value;

        const lowercaseQuery = query.toLowerCase().trim();
        return people.value.filter(person =>
            person.surname.toLowerCase().includes(lowercaseQuery) ||
            person.name.toLowerCase().includes(lowercaseQuery) ||
            person.patronymic.toLowerCase().includes(lowercaseQuery)
        );
    }

    const peopleCount = computed(() => people.value.length);

    return {
        // Состояние
        people,
        error,
        isLoading,

        // Геттеры
        sortedPeople,
        getFormattedName,
        peopleCount,

        // Методы
        clearStore,
        clearError,
        fetchPeople,         // Основная функция фильтрации
        fetchAllPeople,      // Переименованная исходная функция
        fetchActivePeople,   // Новые удобные функции
        fetchDevelopers,
        fetchAssemblers,
        fetchProgrammers,
        fetchTesters,
        fetchAnySpecialists,
        fetchPeopleByCounterparty,
        fetchActiveSpecialists,
        addPerson,
        updatePerson,
        deletePerson,
        getPersonByUuid,
        searchPeople,
    };
});