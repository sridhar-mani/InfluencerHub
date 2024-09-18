<template>
  <div class="w-100">
    <Navbar v-if="userRole !== ''" />
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import Navbar from "./components/Navbar.vue";
import Toast from "./components/Toast.vue";
import router from "./routes";

export default {
  name: "App",
  components: {
    Navbar,
    Toast,
  },
  setup() {
    const userRole = ref("");

    const updateRole = () => {
      userRole.value = localStorage.getItem("role") || "";
    };

    onMounted(updateRole);

    watch(router.currentRoute, updateRole);

    return { userRole };
  },
};
</script>
