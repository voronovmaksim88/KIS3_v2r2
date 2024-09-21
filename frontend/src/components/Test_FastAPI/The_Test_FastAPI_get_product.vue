<script setup>
// Слово "product" в английском языке означает результат умножения двух чисел,
// тогда как "multiplication" относится к самому процессу умножения. То есть:
// - "Product" — это итог (результат) операции (например, 6 является произведением 2 и 3).
// - "Multiplication" — это операция (то, что происходит, когда вы умножаете).
// Поэтому в контексте "произведение двух чисел" правильнее использовать "product".
import {ref, defineProps} from "vue";

const error_get_product = ref(null)
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const mul1 = ref(0) //  множитель 1
const mul2 = ref(0) //  множитель 2
const composition = ref(0) // произведение

async function fetchMultiplication() {
  try {
    // отправляем запрос
    const response = await fetch(`${props.url}test/mult`, {
      method: "POST",
      headers: {"Accept": "application/json", "Content-Type": "application/json"},
      body: JSON.stringify({
        m1: mul1.value,
        m2: mul2.value
      })
    });
    if (response.ok) {
      const data = await response.json();
      composition.value = data.message;
      response_ok.value = "ok";
    } else
      console.log(response);
  } catch (err) {
    error_get_product.value = err.message;
  }
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchMultiplication">Get multiplication</button>
    <div class="flex flex-row gap-2">
      <input
          class="w-1/2 rounded-md"
          type="number"
          v-model="mul1"
          title="Введите первый множитель"
      />
      <input
          class="w-1/2 rounded-md"
          type="number"
          v-model="mul2"
          title="Введите второй множитель"
      />
    </div>

    <p class="text-white">{{ composition }}</p>

    <div v-if="error_get_product">
      <p style="color: red;">{{ error_get_product }}</p>
    </div>

    <div v-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>

  </div>
  <hr class="mb-5">
</template>
