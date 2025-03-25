// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

// Важно: Pinia должна быть установлена ДО использования компонентов,
// в которых используются хранилища
app.use(pinia)

// Другие плагины
// app.use(router)

app.mount('#app')