<script setup>
defineProps({
  message: {
    type: String,
    required: true
  }
});
</script>

<template>
  <div>
    <p class="text-red-400">{{ message }}</p>
  </div>
</template>