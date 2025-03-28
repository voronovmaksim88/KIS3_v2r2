// utils/apiUrlHelper.ts
export function getApiUrl(): string {
    const url = import.meta.env.VITE_API_URL;
    if (!url) {
        console.error('VITE_API_URL не определен в переменных окружения!');
        return 'http://localhost:8000/api'; // Резервный URL по умолчанию
    }
    return url;
}