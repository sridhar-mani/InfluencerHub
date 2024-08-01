<template>
  <div>
    <Navbar v-if="userRole" />
    <router-view />
  </div>
</template>

<script>
import Navbar from "./components/Navbar.vue";

export default {
  name: "App",
  components: {
    Navbar,
  },
  setup() {
    const userRole = localStorage.getItem("role");
    return { userRole };
  },
};
</script>
