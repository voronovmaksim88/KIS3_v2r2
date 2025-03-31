// typeBoxAccounting.ts
import { Person } from './typePerson';

export interface BoxAccounting {
    serial_num: number;
    name: string;
    order_id: string;
    scheme_developer: Person;
    assembler: Person;
    programmer: Person | null;
    tester: Person;
}

export interface PaginatedBoxAccounting {
    items: BoxAccounting[];
    total: number;
    page: number;
    size: number;
    pages: number;
}

// Дополнительные типы для операций со шкафами
export interface BoxAccountingCreateRequest {
    name: string;
    order_id: string; // номер заказа в виде строки типа 001-01-2021
    scheme_developer_id: string; // UUID в виде строки
    assembler_id: string; // UUID в виде строки
    programmer_id?: string | null; // Опциональный UUID
    tester_id: string; // UUID в виде строки
}

// Добавляем интерфейс для ответа API
export interface BoxAccountingResponse {
    serial_num: number;
    name: string;
    order_id: number;
    scheme_developer: {
        uuid: string;
        name: string;
        surname: string;
        patronymic: string;
    };
    assembler: {
        uuid: string;
        name: string;
        surname: string;
        patronymic: string;
    };
    programmer?: {
        uuid: string;
        name: string;
        surname: string;
        patronymic: string;
    };
    tester: {
        uuid: string;
        name: string;
        surname: string;
        patronymic: string;
    };
    order: {
        serial: number;
        name: string;
        // другие поля заказа
    };
}
