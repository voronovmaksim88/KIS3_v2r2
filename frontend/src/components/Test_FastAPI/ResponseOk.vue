<!-- ResponseOk.vue -->
<script setup>
defineProps({
  message: {
    type: String,
    default: 'OK'
  }
});
</script>

<template>
  <div>
    <p class="font-bold text-green-500">{{ message }}</p>
  </div>
</template>