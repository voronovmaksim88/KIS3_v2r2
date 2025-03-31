// src/types/typePerson.ts
export interface Person {
    uuid: string;
    name: string;
    surname: string;
    patronymic: string;
    can_be_scheme_developer: boolean;
    can_be_assembler: boolean;
    can_be_programmer: boolean;
    can_be_tester: boolean;
}