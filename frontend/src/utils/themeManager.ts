// src/utils/themeManager.ts
import { watch } from 'vue';
import { useThemeStore } from '../stores/storeTheme';

export function setupThemeWatcher() {
    const themeStore = useThemeStore();

    // Функция для установки темы PrimeVue
    const updatePrimeVueTheme = (isDark: boolean) => {
        // Удаляем все ссылки на темы PrimeVue
        const links = document.querySelectorAll('link[data-primevue-theme]');
        links.forEach(link => link.remove());

        // Создаем новую ссылку на CSS темы
        const linkElement = document.createElement('link');
        linkElement.rel = 'stylesheet';
        linkElement.href = isDark
            ? '/node_modules/primevue/resources/themes/lara-dark-blue/theme.css'
            : '/node_modules/primevue/resources/themes/lara-light-blue/theme.css';
        linkElement.setAttribute('data-primevue-theme', 'true');

        document.head.appendChild(linkElement);
    };

    // Инициализация темы
    updatePrimeVueTheme(themeStore.theme === 'dark');

    // Наблюдение за изменениями темы
    watch(() => themeStore.theme, (newTheme) => {
        updatePrimeVueTheme(newTheme === 'dark');
    });
}