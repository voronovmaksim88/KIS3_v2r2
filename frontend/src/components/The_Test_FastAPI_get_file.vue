<script setup>
import {ref, defineProps} from "vue";

const error_get_file = ref(null)
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const fetchTestFile = async () => {
  error_get_file.value = null;
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
    error_get_file.value = err.message;
  }
};

</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchTestFile">Load test file</button>

    <div></div>
    <div></div>

    <div v-if="error_get_file">
      <p style="color: red;">{{ error_get_file }}</p>
    </div>

    <div v-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>
  </div>
  <hr class="mb-5">

</template>

<style scoped>

</style>