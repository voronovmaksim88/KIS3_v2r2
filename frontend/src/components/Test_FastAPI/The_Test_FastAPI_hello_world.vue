<script setup>
import {ref} from "vue";
import ResponseOk from './ResponseOk.vue';
import ErrorMessage from './ErrorMessage.vue';

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const error = ref("")
const hello = ref("")
const response_ok = ref("")

const fetchHello = async () => {
  error.value = ''
  response_ok.value = ''
  hello.value = ''
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
      error.value = "Нет ответа от сервера!";
    } else {
      error.value = err.message;
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

    <ErrorMessage v-if="error" :message="error"/>
    <ResponseOk v-if="response_ok" :message="response_ok"/>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>