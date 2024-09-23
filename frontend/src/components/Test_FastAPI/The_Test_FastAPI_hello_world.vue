<script setup>
import {ref} from "vue";

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const errorHello = ref(null)
const hello = ref("")
const response_ok = ref("")

const fetchHello = async () => {
  errorHello.value = null
  response_ok.value = null
  hello.value = ""
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const response = await fetch(`${props.url}test/hello_world`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('Failed to fetch hello message');
    }

    if (response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      response_ok.value = "ok";
    }

    const data = await response.json();
    console.log(data);

    if (data && data.message) {
      hello.value = data.message;
    } else {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('Invalid response format');
    }

  } catch (err) {
    if (err.name === 'AbortError') {
      errorHello.value = "нет ответа от сервера!";
    } else {
      errorHello.value = err.message;
    }
  }
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchHello">Get Hello world</button>

    <div></div>

    <div v-if="hello">
      <p class="text-white">{{ hello }}</p>
    </div>
    <div v-else>
    </div>


    <div v-if="errorHello">
      <p style="color: red;">{{ errorHello }}</p>
    </div>
    <div v-else-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>