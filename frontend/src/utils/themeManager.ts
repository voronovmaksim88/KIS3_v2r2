// src/utils/themeManager.ts
import { watch } from 'vue';
import { useThemeStore } from '../stores/storeTheme';

// Импортируем файлы для их включения в сборку, но не используем возвращаемые значения
// PrimeVue 4.x использует другие пути для тем


export function setupThemeWatcher() {
    const themeStore = useThemeStore();

    const updateTheme = (isDark: boolean) => {
        if (isDark) {
            document.documentElement.classList.add('dark-theme');
        } else {
            document.documentElement.classList.remove('dark-theme');
        }
    };

    updateTheme(themeStore.theme === 'dark');

    watch(() => themeStore.theme, (newTheme) => {
        updateTheme(newTheme === 'dark');
    });
}