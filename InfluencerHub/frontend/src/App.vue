<template>
  <div>
    <Navbar v-if="userRole" />
    <router-view />
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
