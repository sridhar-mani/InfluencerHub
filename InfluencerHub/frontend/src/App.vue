<template>
  <div>
    <Navbar v-if="userRole !== ''" />
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import Navbar from "./components/Navbar.vue";
import Toast from "./components/Toast.vue";
import { useRouter } from "vue-router";

export default {
  name: "App",
  components: {
    Navbar,
    Toast,
  },
  setup() {
    const userRole = ref("");

    const route = useRouter();

    const updateRole = () => {
      userRole.value = localStorage.getItem("role") || ""; // Properly access the reactive reference
      if (userRole.value === "") {
        route.push({ name: "Login" });
      }
    };

    onMounted(updateRole);

    watch(route.currentRoute, updateRole);

    return { userRole }; // Return the reactive reference
  },
};
</script>