import {defineStore} from 'pinia'

type FormType =
    'addRowInBocAccounting'


interface FormsVisibilityState {
    isFormAddRowInBoxAccountingVisible: boolean
}

const formMap = {
    'addRowInBocAccounting': 'isFormAddRowInBocAccounting',
} as const;

export const useFormsVisibilityStore = defineStore('formsVisibility', {
    state: (): FormsVisibilityState => ({
        isFormAddRowInBoxAccountingVisible: false,
    }),

    actions: {
        toggleForm(formType: FormType) {
            const propertyName = formMap[formType] as keyof FormsVisibilityState;
            this[propertyName] = !this[propertyName];

            if (this[propertyName]) {
                this.closeOtherForms(formType);
            }
        },

        closeOtherForms(exceptForm: FormType) {
            Object.entries(this.$state).forEach(([key]) => {
                if (key !== formMap[exceptForm]) {
                    this[key as keyof FormsVisibilityState] = false;
                }
            });
        },

        closeAllForms() {
            Object.keys(this.$state).forEach((key) => {
                this[key as keyof FormsVisibilityState] = false;
            });
        }
    },
})