<script setup>
import { ref } from "vue";
import ResponseOk from './ResponseOk.vue';

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const errorHello = ref("");
const date = ref("");
const time = ref("");
const response_ok = ref("");

const fetchHello = async () => {
  errorHello.value = "";
  response_ok.value = "";
  date.value = "";
  time.value = "";
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const response = await fetch(`${props.url}test/current_datetime`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('Failed to fetch hello message');
    }

    const data = await response.json();
    console.log(data);

    if (data && 'current_datetime' in data) {
      const dateTime = new Date(data.current_datetime);
      date.value = dateTime.toLocaleDateString();
      time.value = dateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      response_ok.value = "ok";
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
    <button class="btn btn-p" @click="fetchHello">Get date time</button>

    <div></div>

    <div v-if="date && time" class="text-white">
      <p>Дата: {{ date }}</p>
      <p>Время: {{ time }}</p>
    </div>
    <div v-else></div>

    <div v-if="errorHello">
      <p class="text-red-500">{{ errorHello }}</p>
    </div>
    <ResponseOk v-if="response_ok" :message="response_ok" />
  </div>
</template>