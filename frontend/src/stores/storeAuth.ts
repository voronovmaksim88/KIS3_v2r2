// stores/storeAuth.ts
import { defineStore } from 'pinia';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrlHelper';

// Добавляем интерфейс для пользователя
interface User {
    username: string;
    // другие поля пользователя, если они есть
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: false,
        user: null as User | null,
    }),

    // Добавляем геттеры
    getters: {
        username: (state) => state.user ? state.user.username : '',
        apiUrl: () => getApiUrl()
    },

    actions: {
        // Добавляем метод setAuthState
        setAuthState(state: boolean) {
            this.isAuthenticated = state;
            if (!state) {
                this.user = null;
            }
        },

        async login(username: string, password: string) {
            try {
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);

                const response = await axios.post(`${this.apiUrl}jwt/login/`, formData, {
                    withCredentials: true // Важно для работы с cookie
                });

                if (response.status === 200) {
                    this.isAuthenticated = true;
                    await this.fetchUserInfo();
                    return true;
                }
            } catch (error) {
                console.error('Login error:', error);
                throw error;
            }
            return false;
        },

        async logout() {
            try {

                // Выполняем запрос на выход
                await axios.post(`${this.apiUrl}jwt/logout/`, {}, {
                    withCredentials: true
                });

                // Очищаем состояние аутентификации
                this.isAuthenticated = false;
                this.user = null;

            } catch (error) {
                console.error('Logout error:', error);
                throw error;
            }
        },

        async fetchUserInfo() {
            try {
                const response = await axios.get(`${this.apiUrl}jwt/users/me/`, {
                    withCredentials: true
                });
                this.user = response.data;
            } catch (error) {
                console.error('Error fetching user info:', error);
                throw error;
            }
        },

        async checkAuth() {
            try {
                await this.fetchUserInfo();
                this.isAuthenticated = true;
            } catch (error) {
                this.isAuthenticated = false;
                this.user = null;
            }
        }
    }
});
