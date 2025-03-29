// src/stores/storeCountries.ts
import { defineStore } from 'pinia';
import { typeCountry } from '../types/typeCountry.ts'; // Убедитесь, что тип экспортируется

export const useStoreCountries = defineStore('storeCountries', {
    // Состояние (state) объявляется как функция
    state: () => ({
        allCountries: [] as typeCountry[], // Типизация массива allCountries
    }),

    // Дополнительно можно добавить actions и getters
    actions: {
        // Пример действия для добавления страны
        addCountry(country: typeCountry) {
            this.allCountries.push(country);
        },
    },

    getters: {
        // Пример геттера для получения количества стран
        countriesCount(): number {
            return this.allCountries.length;
        },
    },
});