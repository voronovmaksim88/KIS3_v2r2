<!-- src/components/FinanceBlock.vue -->
<script setup lang="ts">

// Определение интерфейса для финансовых данных с поддержкой null
interface FinanceData {
  materials_cost?: number | null;
  materials_paid?: boolean | null;
  products_cost?: number | null;
  products_paid?: boolean | null;
  work_cost?: number | null;
  work_paid?: boolean | null;
  debt?: number | null;
  debt_paid?: boolean | null;
}

// Определяем пропсы через деструктуризацию
defineProps<{
  finance: FinanceData | null;
  theme: string;
  detailBlockClass: string;
  detailHeaderClass: string;
  tdBaseTextClass: string;
}>();
</script>

<template>
  <div :class="detailBlockClass">
    <h4 :class="detailHeaderClass">Финансы</h4>

    <div class="grid grid-cols-1 gap-2 text-sm" :class="tdBaseTextClass">
      <!-- Первая строка: Материалы и Товары -->
      <div class="flex justify-between items-center">
        <span>Материалы: </span>
        <span
            class="font-medium text-red-300 min-w-[80px] text-right"
            :class="{ 'line-through opacity-60': finance?.materials_paid }"
        >
          {{ finance?.materials_cost ?? 0 }} руб.
        </span>
      </div>

      <div class="flex justify-between items-center">
        <span>Товары: </span>
        <span
            class="font-medium text-red-300 min-w-[80px] text-right"
            :class="{ 'line-through opacity-60': finance?.products_paid }"
        >
          {{ finance?.products_cost ?? 0 }} руб.
        </span>
      </div>

      <!-- Вторая строка: Работы и Долг -->
      <div class="flex justify-between items-center">
        <span>Работы: </span>
        <span
            class="font-medium text-red-300 min-w-[80px] text-right"
            :class="{ 'line-through opacity-60': finance?.work_paid }"
        >
          {{ finance?.work_cost ?? 0 }} руб.
        </span>
      </div>

      <div class="flex justify-between items-center">
        <span>Нам должны: </span>
        <span
            class="font-medium text-green-400 min-w-[80px] text-right"
            :class="{ 'line-through opacity-60': finance?.debt_paid }"
        >
          {{ finance?.debt ?? 0 }} руб.
        </span>
      </div>
    </div>
  </div>
</template>