<script setup>
import {ref} from "vue";
import ResponseOk from './ResponseOk.vue';
import ErrorMessage from './ErrorMessage.vue';

const error = ref("")
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
    error.value = ''
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
    error.value = err.message;
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

    <ErrorMessage v-if="error" :message="error"/>
    <ResponseOk v-if="response_ok" :message="response_ok"/>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>