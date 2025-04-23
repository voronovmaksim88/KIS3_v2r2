// store/storeTheme.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ThemeMode = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
    const theme = ref<ThemeMode>('light')

    function setTheme(newTheme: ThemeMode) {
        theme.value = newTheme
        document.documentElement.classList.toggle('dark', newTheme === 'dark')
        localStorage.setItem('theme', newTheme)
    }

    function toggleTheme() {
        const newTheme: ThemeMode = theme.value === 'light' ? 'dark' : 'light'
        setTheme(newTheme)
    }

    // При запуске пытаемся прочитать из localStorage
    // function initTheme() {
    //     const stored = localStorage.getItem('theme') as ThemeMode | null
    //     if (stored === 'dark' || stored === 'light') {
    //         setTheme(stored)
    //     } else {
    //         // Или используем prefers-color-scheme
    //         const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    //         setTheme(prefersDark ? 'dark' : 'light')
    //     }
    // }

    return {
        theme,
        toggleTheme,
    }
})