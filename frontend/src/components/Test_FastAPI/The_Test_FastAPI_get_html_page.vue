<script setup>
import {ref} from "vue";
import ResponseOk from './ResponseOk.vue';
import ErrorMessage from './ErrorMessage.vue';

const error = ref("")
const htmlContent = ref('')
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const fetchTestHTMLPage = async () => {
  error.value = ''
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
    error.value = err.message;
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

    <ErrorMessage v-if="error" :message="error"/>
    <ResponseOk v-if="response_ok" :message="response_ok"/>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>