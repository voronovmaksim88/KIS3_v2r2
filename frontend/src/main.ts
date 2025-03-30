// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';
// Попробуйте импортировать тёмную версию Aura




const app = createApp(App)
const pinia = createPinia()

// Важно: Pinia должна быть установлена ДО использования компонентов,
// в которых используются хранилища
app.use(pinia)


// Используйте PrimeVue
app.use(PrimeVue, {
    // Default theme configuration
    theme: {
        preset: Aura,
        dark: true
    }
});

// Другие плагины
// app.use(router)

app.mount('#app')