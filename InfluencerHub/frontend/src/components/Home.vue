<template>
  <div class="d-flex w-100 h-100 flex-column"></div>
</template>

<script>
import router from "../routes";

export default {
  name: "Home",
  setup() {
    const role = localStorage.getItem("role");
    if (!role) {
      router.push({ name: "Login" });
    }
  },
};
</script>

<style scoped></style>
