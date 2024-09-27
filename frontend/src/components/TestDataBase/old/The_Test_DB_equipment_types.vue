<script setup>
import {ref} from 'vue'

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

// функция получает список всех производителей из БД PostgreSQL
const all_equipment_types = ref("") // список всех стран
const connection_error = ref("") // список всех стран
async function fetchEquipment_types() {
  connection_error.value = '';
  all_equipment_types.value = ""; // изначально обнуляем список стран
  const timeout = 3000; // 3 секунды
  const fetchPromise = fetch(`${props.url}all_equipment_types`);
  const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timed out')), timeout)
  );

  /**
   * @typedef {Object} ServerResponse
   * @property {string[]} manufacturers
   */

  /**
   * @param {ServerResponse} data
   */
  try {
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    console.log('Response status:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Received data:', data);
      if ('equipment_types' in data) {
        all_equipment_types.value = data.equipment_types;
      }

      connection_error.value = ""; // если получен ответ скидываем ошибку
    } else {
      console.log('Response not OK:', response);
    }
  } catch (error) {
    if (error.message === 'Request timed out') {
      console.error('Request timed out after', timeout, 'ms');
    } else {
      console.error('Error fetching countries:', error);
    }
    connection_error.value = error.message;
    all_equipment_types.value = "";
  }
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">

    <div class="col-span-4">
      <button class="btn btn-p " @click="fetchEquipment_types">Get Equipment types from DB</button>
    </div>

    <div class="col-span-4" v-if="all_equipment_types && all_equipment_types.length > 0">
      <table>
        <thead>
        <tr>
          <th>id</th>
          <th>name</th>
        </tr>
        </thead>
        <tr v-for="equipment_type in all_equipment_types" :key="equipment_type.id">
          <td>{{ equipment_type.id }}</td>
          <td>{{ equipment_type.name }}</td>
        </tr>
      </table>
    </div>
    <p class="text-red-400 col-span-4" v-if="connection_error">{{ connection_error }}</p>
    <hr class="col-span-4 mb-8"> <!-- Обратите внимание, что мы добавили col-span-4 для лучшего управления отступом -->

  </div>
</template>

<style scoped>

</style>