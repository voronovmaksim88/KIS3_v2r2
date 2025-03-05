<script setup>
import {ref} from "vue";
import ResponseOk from './ResponseOk.vue';
import ErrorMessage from './ErrorMessage.vue';

const userName = ref("")
const helloName = ref("")
const error = ref("")
const input_name_class = ref("border-2 rounded-md")
const input_error_style = "border-2 border-red-500 rounded-md focus:outline-none focus:ring-2"
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const fetchHelloName = async () => {
  error.value = ''
  if (userName.value) {
    try {
      const response = await fetch(`${props.url}test/hello?name=${encodeURIComponent(userName.value)}`);

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
        helloName.value = data.message;
      } else {
        // noinspection ExceptionCaughtLocallyJS
        throw new Error('Invalid response format');
      }

    } catch (err) {
      error.value = err.message;

    }
  } else {
    // alert("введите имя")
    input_name_class.value = input_error_style
    helloName.value = ''
  }
}

const resetInputClassDynamic = (inputName) => {
  if (inputName === 'userName') {
    input_name_class.value = "border-2 rounded-md";
  }
};
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchHelloName">Get Hello Name</button>
    <input
        id="input_name"
        type="text"
        v-model="userName"
        placeholder="Enter user name"
        :class="input_name_class"
        @focus="resetInputClassDynamic('userName')"
    />
    <p class="text-white">{{ helloName }}</p>
    <ErrorMessage v-if="error" :message="error"/>
    <ResponseOk v-if="response_ok" :message="response_ok"/>
  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>