<script setup>

import Test_DB_universal_table from "./Test_DB_universal_table.vue";

// const backend_url = "https://sibplc-kis3.ru/api/"
// const backend_url = "http://localhost:8000/api/"
const backend_url = import.meta.env.VITE_API_URL; // Если используете Vite


</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800" id="BD_FastAPI_PostGreSQL">
    <div class="flex flex-col w-full sm:w-1/2 md:w-2/3 lg:w-2/3 xl:w-10/12 space-y-4">
      <h1 class="text-green-400 text-3xl mb-5">Test Data Base</h1>

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_countries"
          buttonText="Страны"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_manufacturers"
          buttonText="Производителей"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_equipment_types"
          buttonText="Типы оборудования"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_currencies"
          buttonText="Валюты"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_cities"
          buttonText="Города"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_counterparty_forms"
          buttonText="Формы контрагентов"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_counterparties"
          buttonText="Контрагенты"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_people"
          buttonText="Люди"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_works"
          buttonText="Работы"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_order_statuses"
          buttonText="Статусы заказов"
      />

      <Test_DB_universal_table
          :url="backend_url"
          endpoint="all_orders"
          buttonText="Заказы"
      />

      <!-- Добавляем отступ после последней таблицы -->
      <div class="h-16"></div>

    </div>

  </div>
</template>

<style scoped>

</style>