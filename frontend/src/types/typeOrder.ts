// src/type/typeOrder.ts
export interface typeOrderSerial {
    serial: string;
}

// Новый тип для одного заказа (соответствует Pydantic OrderRead)
export interface typeOrderRead {
    serial: string;
    name: string;
    customer: string; // Ожидаем строку 'Форма Имя'
    priority: number | null;
    status_id: number;
    start_moment: string | null; // Даты приходят как строки ISO 8601
    deadline_moment: string | null;
    end_moment: string | null;
    materials_cost: number | null;
    materials_paid: boolean;
    products_cost: number | null;
    products_paid: boolean;
    work_cost: number | null;
    work_paid: boolean;
    debt: number | null;
    debt_paid: boolean;
}

// Новый тип для ответа API с пагинацией (соответствует Pydantic PaginatedOrderResponse)
export interface typePaginatedOrderResponse {
    total: number;
    limit: number;
    skip: number;
    data: typeOrderRead[];
}

// Новый тип для параметров запроса fetchOrders
export interface typeFetchOrdersParams {
    skip?: number;
    limit?: number;
    statusId?: number | null;
    searchSerial?: string | null;
    searchCustomer?: string | null;
    searchPriority?: number | null;
}
