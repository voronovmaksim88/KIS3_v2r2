// stores/storeAuth.ts
import { defineStore } from 'pinia'
import axios from 'axios'


// Добавляем интерфейс для пользователя
interface User {
    username: string;
    // другие поля пользователя, если они есть
}

export const useAuthStore = defineStore('auth', {

    state: () => ({
        isAuthenticated: false,
        user: null as User | null  // Указываем тип для user
    }),

    // Добавляем геттеры
    getters: {
        username: (state) => state.user ? state.user.username : ''
    },

    actions: {
        // Добавляем метод setAuthState
        setAuthState(state: boolean) {
            this.isAuthenticated = state
            if (!state) {
                this.user = null
            }
        },

        async login(username: string, password: string, apiUrl: string) {
            try {
                const formData = new FormData()
                formData.append('username', username)
                formData.append('password', password)

                const response = await axios.post(`${apiUrl}jwt/login/`, formData, {
                    withCredentials: true // Важно для работы с cookie
                })

                if (response.status === 200) {
                    this.isAuthenticated = true
                    await this.fetchUserInfo(apiUrl)
                    return true
                }
            } catch (error) {
                console.error('Login error:', error)
                throw error
            }
            return false
        },

        async logout(apiUrl: string) {
            try {
                // Получаем экземпляры store для задач и проектов
                // const taskStore = useTaskStore()
                // const projectStore = useProjectsStore()

                // Выполняем запрос на выход
                await axios.post(`${apiUrl}/jwt/logout/`, {}, {
                    withCredentials: true
                })

                // Очищаем состояние аутентификации
                this.isAuthenticated = false
                this.user = null

                // Очищаем списки задач и проектов
                // taskStore.allTasks = []
                // projectStore.allProjects = []
            } catch (error) {
                console.error('Logout error:', error)
                throw error
            }
        },

        async fetchUserInfo(apiUrl: string) {
            try {
                const response = await axios.get(`${apiUrl}/jwt/users/me/`, {
                    withCredentials: true
                })
                this.user = response.data
            } catch (error) {
                console.error('Error fetching user info:', error)
                throw error
            }
        },

        async checkAuth(apiUrl: string) {
            try {
                await this.fetchUserInfo(apiUrl)
                this.isAuthenticated = true
            } catch (error) {
                this.isAuthenticated = false
                this.user = null
            }
        }
    }
})
