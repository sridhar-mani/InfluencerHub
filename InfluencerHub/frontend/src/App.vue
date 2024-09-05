<template>
  <div>
    <Navbar v-if="userRole !== null" />
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import Navbar from "./components/Navbar.vue";
import Toast from "./components/Toast.vue";

export default {
  name: "App",
  components: {
    Navbar,
    Toast,
  },
  setup() {
    const userRole = ref("");

    onMounted(() => {
      userRole.value = localStorage.getItem("role");
    });

    return { userRole };
  },
};
</script>
