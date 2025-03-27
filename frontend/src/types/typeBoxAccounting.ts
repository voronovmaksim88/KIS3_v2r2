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
    order_id: string;
    scheme_developer_id: string;
    assembler_id: string;
    programmer_id?: string; // Опциональное поле
    tester_id: string;
}

export interface BoxAccountingUpdateRequest {
    name: string;
    order_id: string;
    scheme_developer_id: string;
    assembler_id: string;
    programmer_id?: string; // Опциональное поле
    tester_id: string;
}