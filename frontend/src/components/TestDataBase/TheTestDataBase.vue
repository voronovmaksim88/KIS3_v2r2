<script setup>

import Test_DB_universal_table from "./Test_DB_universal_table.vue";

// const backend_url = "https://sibplc-kis3.ru/api/"
// const backend_url = "http://localhost:8000/api/"
const backend_url = import.meta.env.VITE_API_URL; // Если используете Vite


</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800" id="BD_FastAPI_PostGreSQL">
    <div class="flex flex-col w-full sm:w-1/1 md:w-2/3 lg:w-2/3 xl:w-10/12 space-y-4">

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_countries"
          importName="countries"
          buttonText="Страны"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_cities"
          importName="cities"
          buttonText="Города"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_currencies"
          importName="currencies"
          buttonText="Валюты"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_equipment_types"
          importName="equipment_types"
          buttonText="Типы оборудования"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_counterparty_forms"
          importName="counterparty_forms"
          buttonText="Формы контрагентов"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_counterparties"
          importName="companies"
          buttonText="Контрагенты"
      />












      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_manufacturers"
          importName="manufacturers"
          buttonText="Производители"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_people"
          importName="people"
          buttonText="Люди"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_works"
          importName="works"
          buttonText="Работы"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_order_statuses"
          importName="order_statuses"
          buttonText="Статусы заказов"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_orders"
          importName="orders"
          buttonText="Заказы"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_order_comments"
          importName="order_comments"
          buttonText="Комментарии к заказам"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_control_cabinets"
          importName="boxes"
          buttonText="корпуса шкафов"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_box_accounting"
          importName="box_accounting"
          buttonText="записи о серийных номерах"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_tasks"
          importName="tasks"
          buttonText="задачи"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_timings"
          importName="timings"
          buttonText="тайминги"
      />

      <!-- Добавляем отступ после последней таблицы -->
      <div class="h-16"></div>

    </div>

  </div>
</template>

<style scoped>

</style>