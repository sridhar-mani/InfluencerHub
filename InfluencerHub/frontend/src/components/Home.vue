<template>
  <Teleport to="body">
    <div :class="'top-0 end-0'" class="toast-container position-fixed p-3">
      <BToast v-model="showToast">
        <template #title>{{ message }}</template>
        {{ message }}
      </BToast>
    </div>
  </Teleport>
</template>

<script>
import { onMounted, ref } from "vue";
import router from "../routes.ts";

export default {
  name: "Home",
  setup() {
    const showToast = ref(false);
    const message = ref("");

    onMounted(() => {
      const role = localStorage.getItem("role");
      if (!role) {
        router.push({ name: "Login" });
      }
      if (localStorage.getItem("role") === "admin") {
        message.value = "Admin login successful";
        showToast.value = true;
      } else {
        message.value = "Welcome " + localStorage.username;
        showToast.value = true;
      }
    });
    return { showToast, message };
  },
};
</script>

<style scoped></style>
