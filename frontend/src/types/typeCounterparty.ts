// typeCounterparty.ts

// Интерфейс для формы контрагента
export interface CounterpartyForm {
    id: number;
    name: string;
}

// Интерфейс для контрагента
export interface Counterparty {
    id: number;
    name: string;
    form: CounterpartyForm;
}

// Состояние хранилища Pinia для контрагентов
export interface CounterpartyState {
    counterparties: Counterparty[];
    loading: boolean;
    error: string | null;
}