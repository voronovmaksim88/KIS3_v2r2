<script setup>
import {ref} from "vue";

const error = ref(null)
const input_startId_class = ref("border-2 rounded-md")
const input_qty_class = ref("border-2 rounded-md")
const input_error_style = "border-2 border-red-500 rounded-md focus:outline-none focus:ring-2"
const response_ok = ref("")
const start_ID = ref("1")
const order_qty = ref("1")
const orders = ref(null)

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const fetchUser = async () => {
  error.value = null
  orders.value = null
  response_ok.value = null
  if (start_ID.value && order_qty.value) {
    try {
      // Формируем URL для запроса
      const offset = start_ID.value - 1; // Поскольку start_ID начинается с 1, нужно уменьшить на 1 для offset
      const limit = order_qty.value;
      const response = await fetch(`${props.url}test/order?offset=${offset}&limit=${limit}`);

      if (response.ok) {
        // noinspection ExceptionCaughtLocallyJS
        response_ok.value = "ok";
      }

      if (!response.ok) {
        // noinspection ExceptionCaughtLocallyJS
        throw new Error('Order not found!!!');
      }

      const data = await response.json();
      console.log(data);

      orders.value = data;
    } catch (err) {
      error.value = err.message;
    }
  } else {
    input_startId_class.value = input_error_style
  }
}

const resetInputClassDynamic = (inputName) => {
  if (inputName === 'start_ID') {
    input_startId_class.value = "border-2 rounded-md";
  }
  if (inputName === 'start_ID') {
    input_qty_class.value = "border-2 rounded-md";
  }
};

</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchUser">Fetch fake order</button>
    <div class="flex flex-row gap-2">
      <input
          class="w-1/2 rounded-md"
          type="number"
          v-model="start_ID"
          title="Введите начальный id заказов"
          placeholder="start ID"
          @focus="resetInputClassDynamic('start_ID')"
      />
      <input
          class="w-1/2 rounded-md"
          type="number"
          v-model="order_qty"
          title="Введите количество  заказов"
          placeholder="qty"
          @focus="resetInputClassDynamic('order_qty')"
      />
    </div>

    <div class="text-white" v-if="orders">
      <p v-for="order in orders" :key="order.id">{{ order }}</p>
    </div>
    <div v-else>
    </div>

    <div v-if="error">
      <p style="color: red;">{{ error }}</p>
    </div>

    <div v-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>