// stores/storePage.ts
import {defineStore} from 'pinia';

interface Tab {
    id: string;
    label: string;
}

export const usePagesStore = defineStore('tabs', {
    state: () => ({
        selectedPage: 'main',  // по умолчанию показываем вкладку "задачи"
        tabs: [
            {id: 'main', label: 'Задачи'},
            {id: 'task', label: 'Задачи'},
            {id: 'order', label: 'Заказы'},
            {id: 'timings', label: 'Тайминги'},
            {id: 'box-serial-num', label: 'Учёт с/н ША'},
            {id: 'test-fastapi', label: 'Тесты FastAPI'},
            {id: 'test-db', label: 'Тесты БД>'},
        ] as Tab[],
    }),
    actions: {
        setPage(id: string) {
            if (this.tabs.find((tab) => tab.id === id)) {
                this.selectedPage = id;
            } else {
                console.error(`Вкладки с идентификатором ${id} не существует.`);
            }
        },
    }
});