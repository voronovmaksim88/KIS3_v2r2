// src/store/storeWorks.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { typeWork } from '@/types/typeWork'
import { getApiUrl } from '../utils/apiUrlHelper';

export const useWorksStore = defineStore('works', () => {
    // State
    const works = ref<typeWork[]>([])
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Getters
    const activeWorks = computed(() => works.value.filter(work => work.active))
    const sortedWorks = computed(() => [...works.value].sort((a, b) => a.name.localeCompare(b.name)))
    const getWorkById = (id: number) => works.value.find(work => work.id === id)

    // Actions
    const fetchWorks = async () => {
        isLoading.value = true
        error.value = null

        try {
            const response = await axios.get(`${getApiUrl()}works/read-active`)
            works.value = response.data
        } catch (err) {
            console.error('Ошибка при получении списка работ:', err)
            error.value = err instanceof Error ? err.message : 'Неизвестная ошибка при загрузке работ'
        } finally {
            isLoading.value = false
        }
    }

    // const addWork = async (newWork: Omit<typeWork, 'id'>) => {
    //     isLoading.value = true
    //     error.value = null
    //
    //     try {
    //         const response = await axios.post('/api/works', newWork)
    //         works.value.push(response.data)
    //     } catch (err) {
    //         console.error('Ошибка при добавлении работы:', err)
    //         error.value = err instanceof Error ? err.message : 'Неизвестная ошибка при добавлении работы'
    //         throw err
    //     } finally {
    //         isLoading.value = false
    //     }
    // }
    //
    // const updateWork = async (id: number, updatedWork: Partial<typeWork>) => {
    //     isLoading.value = true
    //     error.value = null
    //
    //     try {
    //         const response = await axios.patch(`/api/works/${id}`, updatedWork)
    //         const index = works.value.findIndex(work => work.id === id)
    //         if (index !== -1) {
    //             works.value[index] = { ...works.value[index], ...response.data }
    //         }
    //     } catch (err) {
    //         console.error('Ошибка при обновлении работы:', err)
    //         error.value = err instanceof Error ? err.message : 'Неизвестная ошибка при обновлении работы'
    //         throw err
    //     } finally {
    //         isLoading.value = false
    //     }
    // }

    // const toggleWorkStatus = async (id: number) => {
    //     const work = getWorkById(id)
    //     if (work) {
    //         await updateWork(id, { active: !work.active })
    //     }
    // }

    return {
        // State
        works,
        isLoading,
        error,

        // Getters
        activeWorks,
        sortedWorks,
        getWorkById,

        // Actions
        fetchWorks,
        //addWork,
        //updateWork,
        //toggleWorkStatus
    }
})