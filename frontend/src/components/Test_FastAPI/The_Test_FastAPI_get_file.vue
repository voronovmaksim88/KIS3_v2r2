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

const fetchTestFile = async () => {
  error.value = ''
  try {
    const response = await fetch(`${props.url}test/load_test_file`);

    if (!response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('test_file not found!!!');
    }

    if (response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      response_ok.value = "ok";
    }

    // Здесь нужно добавить обработку успешного ответа
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = 'test_file.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);

  } catch (err) {
    error.value = err.message;
  }
};

</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchTestFile">Load test file</button>

    <div></div>
    <div></div>

    <ErrorMessage v-if="error" :message="error"/>
    <ResponseOk v-if="response_ok" :message="response_ok"/>
  </div>
  <hr class="mb-5">

</template>

<style scoped>

</style>