<script setup>

import The_Test_FastAPI_hello_world from "@/components/Test_FastAPI/The_Test_FastAPI_hello_world.vue";
import The_Test_FastAPI_hello_name from "@/components/Test_FastAPI/The_Test_FastAPI_hello_name.vue";
import The_Test_FastAPI_fetch_fake_user from "@/components/Test_FastAPI/The_Test_FastAPI_fetch_fake_user.vue";
import The_Test_FastAPI_get_html_page from "@/components/Test_FastAPI/The_Test_FastAPI_get_html_page.vue";
import The_Test_FastAPI_get_file from "@/components/Test_FastAPI/The_Test_FastAPI_get_file.vue";
import The_Test_FastAPI_get_sum from "@/components/Test_FastAPI/The_Test_FastAPI_get_sum.vue";
import The_Test_FastAPI_get_product from "@/components/Test_FastAPI/The_Test_FastAPI_get_product.vue";
import The_Test_FastAPI_change_user_name from "@/components/Test_FastAPI/The_Test_FastAPI_change_user_name.vue";

// const backend_url = "https://sibplc-kis3.ru/api/"
const backend_url = "http://localhost:8000/api/"

</script>

<template>
  <div class="w-full min-h-screen flex flex-col items-center bg-gray-800" id="BD_FastAPI_PostGreSQL">
    <div class="flex flex-col w-full sm:w-1/2 md:w-2/3 lg:w-2/3 xl:w-5/12 space-y-4">
      <h1 class="text-green-400 text-3xl mb-5">Test FastApi</h1>

      <The_Test_FastAPI_hello_world :url="backend_url"/>
      <The_Test_FastAPI_hello_name :url="backend_url"/>
      <The_Test_FastAPI_fetch_fake_user :url="backend_url"/>
      <The_Test_FastAPI_change_user_name :url="backend_url"/>
      <The_Test_FastAPI_get_html_page :url="backend_url"/>
      <The_Test_FastAPI_get_file :url="backend_url"/>
      <The_Test_FastAPI_get_sum :url="backend_url"/>
      <The_Test_FastAPI_get_product :url="backend_url"/>


    </div>
  </div>
</template>

<style scoped>

</style>