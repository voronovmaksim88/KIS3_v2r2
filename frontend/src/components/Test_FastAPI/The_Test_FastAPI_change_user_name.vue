<script setup>
import {ref, defineProps, computed} from "vue";

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

function ChangeUserName() {

}

</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <button class="btn btn-p" @click="ChangeUserName">Change user name</button>
    <input
        type="number"
        v-model="userId"
        placeholder="Enter user ID"
        :class="input_userId_class"
        @focus="resetInputClassDynamic('userId')"
    />

    <div class="text-white" v-if="user">
    </div>
    <div v-else>
    </div>

    <div v-if="error_user">
      <p style="color: red;">{{ error_user }}</p>
    </div>

    <div v-if="response_ok">
      <p class="font-bold text-green-500">{{ response_ok }}</p>
    </div>

  </div>
  <hr class="mb-5">
</template>

<style scoped>

</style>