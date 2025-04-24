// store/storeTheme.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ThemeMode = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
    const theme = ref<ThemeMode>('light')

    function setTheme(newTheme: ThemeMode) {
        theme.value = newTheme

        // Обновляем класс dark для Tailwind
        document.documentElement.classList.toggle('dark', newTheme === 'dark')

        // Обновляем класс my-app-dark для вашего приложения
        document.documentElement.classList.toggle('my-app-dark', newTheme === 'dark')

        // Сохраняем в localStorage
        localStorage.setItem('theme', newTheme)
    }

    function toggleTheme() {
        const newTheme: ThemeMode = theme.value === 'light' ? 'dark' : 'light'
        setTheme(newTheme)
    }

    // Инициализация темы при запуске приложения
    function initTheme() {
        const stored = localStorage.getItem('theme') as ThemeMode | null
        if (stored === 'dark' || stored === 'light') {
            setTheme(stored)
        } else {
            // Используем системные настройки через prefers-color-scheme
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
            setTheme(prefersDark ? 'dark' : 'light')
        }
    }

    return {
        theme,
        setTheme,
        toggleTheme,
        initTheme
    }
})