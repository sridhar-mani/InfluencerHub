<template>
  <div class="w-100">
    <Teleport to="body">
      <div :class="'top-0 end-0'" class="toast-container position-fixed p-3">
        <BToast v-model="showToast" class="specialPop">
          <template #title>{{ message }}</template>
          {{ message }}
        </BToast>
      </div>
    </Teleport>
    <router-view></router-view>
  </div>
</template>

<script>
import { onMounted, ref } from "vue";

export default {
  name: "Home",
  setup() {
    const showToast = ref(false);
    const message = ref("");

    onMounted(() => {
      const role = localStorage.getItem("role");
      if (role === "admin") {
        message.value = "Admin login successful";
      } else {
        message.value = "Welcome " + localStorage.getItem("username");
      }
      showToast.value = true;
      const toastComp = document.getElementsByClassName("specialPop")[0];
      toastComp.style.backgroundColor = "green";
    });

    return { showToast, message };
  },
};
</script>

<style scoped></style>
