// src/type/typeTask.ts

export interface typeTask {
    id: number;
    name: string;
    description: string;
    status_id: number;
    payment_status_id: number;
    executor_id: string | null;
    planned_duration: string | null;
    actual_duration: string | null;
    creation_moment: string;
    start_moment: string;
    deadline_moment: string;
    end_moment: string | null;
    price: number | null;
    parent_task_id: number | null;
    root_task_id: number | null;
}