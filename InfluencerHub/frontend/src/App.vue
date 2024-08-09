<template>
  <div>
    <Navbar v-if="userRole" />
    <router-view />
    <ToastComponent ref="toast" />
  </div>
</template>

<script>
import Navbar from "./components/Navbar.vue";
import Toast from "./components/Toast.vue";

export default {
  name: "App",
  components: {
    Navbar,
    Toast,
  },
  setup() {
    const userRole = localStorage.getItem("role");
    return { userRole };
  },
};
</script>
