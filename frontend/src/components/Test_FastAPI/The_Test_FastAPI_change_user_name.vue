<script setup>
import {ref} from "vue";
import ResponseOk from './ResponseOk.vue';
import ErrorMessage from './ErrorMessage.vue';

const user = ref(null)
const userId = ref(null)
const error = ref("")
const input_userId_class = ref("border-2 rounded-md")
const input_new_name_class = ref("border-2 rounded-md")
const input_error_style = "border-2 border-red-500 rounded-md focus:outline-none focus:ring-2"
const response_ok = ref("")
const new_name = ref(null)


const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

async function ChangeUserName() {
  if (userId.value && new_name.value) {
    try {
      error.value = ''
      // отправляем запрос
      const response = await fetch(`${props.url}test/change_user_name/${userId.value}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_name: new_name.value
        })
      });

      if (response.ok) {
        // noinspection ExceptionCaughtLocallyJS
        response_ok.value = "ok";
      }

      if (!response.ok) {
        // noinspection ExceptionCaughtLocallyJS
        throw new Error('User not found!!!');
      }

      const data = await response.json();
      console.log(data);


    } catch (err) {
      error.value = err.message;
    }

  } else {
    if (!new_name.value) {
      input_new_name_class.value = input_error_style
    }
    if (!userId.value) {
      input_userId_class.value = input_error_style
    }
  }

}

const resetInputClassDynamic = (inputName) => {
  if (inputName === 'userId') {
    input_userId_class.value = "border-2 rounded-md";
  }
  if (inputName === 'new_name') {
    input_new_name_class.value = "border-2 rounded-md";
  }
};


</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="ChangeUserName">Change user name</button>
    <div class="flex flex-row gap-2">
      <input
          class="w-1/2 rounded-md"
          :class="input_userId_class"
          type="number"
          v-model="userId"
          placeholder="user ID"
          @focus="resetInputClassDynamic('userId')"
      />

      <input
          class="w-1/2 rounded-md"
          :class="input_new_name_class"
          type="text"
          v-model="new_name"
          placeholder="new name"
          @focus="resetInputClassDynamic('new_name')"
      />
    </div>

    <div class="text-white" v-if="user">
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