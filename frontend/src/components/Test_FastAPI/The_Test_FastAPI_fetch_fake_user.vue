<script setup>
import {ref, computed} from "vue";
import ResponseOk from './ResponseOk.vue';

const user = ref(null)
const userId = ref(null)
const error_user = ref(null)
const input_userId_class = ref("border-2 rounded-md")
const input_error_style = "border-2 border-red-500 rounded-md focus:outline-none focus:ring-2"
const response_ok = ref("")

const props = defineProps({
  url: {
    type: String,
    required: true
  }
});

const fetchUser = async () => {
  user.value = null;
  error_user.value = null;
  if (userId.value) {
    try {
      const response = await fetch(`${props.url}test/get_user/${userIdNumber.value}`);

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

      user.value = data;
    } catch (err) {
      error_user.value = err.message;
    }
  } else {
    // alert("введите имя")
    input_userId_class.value = input_error_style
  }
}

const resetInputClassDynamic = (inputName) => {
  if (inputName === 'userId') {
    input_userId_class.value = "border-2 rounded-md";
  }
};

// Вычисляемое свойство лучше определить за пределами функции
const userIdNumber = computed(() => parseInt(userId.value));

</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="fetchUser">Fetch fake user by id</button>
    <input
        type="number"
        v-model="userId"
        placeholder="Enter user ID"
        :class="input_userId_class"
        @focus="resetInputClassDynamic('userId')"
    />

    <div class="text-white" v-if="user">
      <h2>User Info</h2>
      <p>ID: {{ user.id }}</p>
      <p>Name: {{ user.name }}</p>
      <!--suppress JSUnresolvedReference -->
      <p>Age: {{ user.age }}</p>
    </div>
    <div v-else>
    </div>

    <div v-if="error_user">
      <p style="color: red;">{{ error_user }}</p>
    </div>

    <ResponseOk v-if="response_ok" :message="response_ok" />

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>