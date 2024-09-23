<script setup>
import {ref} from "vue";

const error_get_sum = ref(null)
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const a = ref(0)
const b = ref(0)
const c = ref(0)

async function getSumma() {
  try {
    error_get_sum.value = null;
    // отправляем запрос
    const response = await fetch(`${props.url}test/summa`, {
      method: "POST",
      headers: {"Accept": "application/json", "Content-Type": "application/json"},
      body: JSON.stringify({
        a: a.value,
        b: b.value
      })
    });
    if (response.ok) {
      const data = await response.json();
      c.value = data.message;
      response_ok.value = "ok";
    } else
      console.log(response);
  } catch (err) {
    error_get_sum.value = err.message;
  }
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="getSumma">Get sum</button>
    <div class="flex flex-row gap-2">
      <input
          class="w-1/2 rounded-md"
          type="number"
          v-model="a"
          title="Введите первое слагаемое"
      />
      <input
          class="w-1/2 rounded-md"
          type="number"
          v-model="b"
          title="Введите второе слагаемое"
      />
    </div>
    <p class="text-white">{{ c }}</p>

    <div v-if="error_get_sum">
      <p style="color: red;">{{ error_get_sum }}</p>
    </div>

    <div v-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>