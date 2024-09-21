<script setup>
import {ref, defineProps} from "vue";

const error_TestHTMLPage = ref(null)
const htmlContent = ref('')
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const fetchTestHTMLPage = async () => {
  error_TestHTMLPage.value = null;
  htmlContent.value = null;
  try {
    const response = await fetch(`${props.url}test/load_test_html_page`);

    if (!response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      throw new Error('test_html_page not found!!!');
    }

    if (response.ok) {
      // noinspection ExceptionCaughtLocallyJS
      response_ok.value = "ok";
    }

    htmlContent.value = await response.text();
  } catch (err) {
    error_TestHTMLPage.value = err.message;
  }
};
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchTestHTMLPage">Get HTML page</button>

    <div v-if="htmlContent" class="col-span-2">
      <div v-html="htmlContent" class="bg-white p-4 rounded-md"></div>
    </div>
    <div v-else class="col-span-2">
    </div>

    <div v-if="error_TestHTMLPage">
      <p style="color: red;">{{ error_TestHTMLPage }}</p>
    </div>

    <div v-else-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>