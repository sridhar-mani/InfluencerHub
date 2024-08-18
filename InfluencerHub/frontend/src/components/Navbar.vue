<template>
  <BNavbar
    toggleable="lg"
    variant="Light"
    v-b-color-mode="'dark'"
    class="border-bottom-1"
  >
    <BNavbarBrand v-if="userRole === 'admin'"> Admin's Dashboard </BNavbarBrand>
    <BNavbarBrand v-else-if="userRole === 'influencer'">
      Influencer's Dashboard
    </BNavbarBrand>
    <BNavbarBrand v-else> Sponsor's Dashboard </BNavbarBrand>

    <BNavbarToggle target="nav-collapse" />
    <BCollapse id="nav-collapse" is-nav>
      <BNavbarNav>
        <BNavItem v-if="userRole === 'admin'" :to="{ name: 'Info' }">
          Info
        </BNavItem>
        <BNavItem v-if="userRole === 'sponsor'" :to="{ name: 'Campaign' }">
          Campaigns
        </BNavItem>
        <BNavItem v-if="userRole" :to="{ name: 'Find' }"> Find </BNavItem>
        <BNavItem v-if="userRole" :to="{ name: 'Stats' }"> Stats </BNavItem>
      </BNavbarNav>

      <BNavbarNav class="ms-auto mb-2 mb-lg-0">
        <BNavItemDropdown right>
          <template #button-content>
            <BAvatar rounded="circle" size="1.5em" class="mx-1" />
            <b>{{ userName }}</b>
          </template>
          <BDropdownItem
            v-if="userRole === 'influencer' || userRole === 'sponsor'"
            :to="{ name: 'Profile' }"
          >
            Profile
          </BDropdownItem>
          <BDropdownItem @click="signout"> Sign Out </BDropdownItem>
        </BNavItemDropdown>
      </BNavbarNav>
    </BCollapse>
  </BNavbar>
</template>

<script>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

export default {
  name: "Navbar",
  setup() {
    const userRole = ref("");
    const userName = ref("");
    const router = useRouter();

    const checkSession = () => {
      const isUserLoggedIn = localStorage.getItem("username") !== null;

      if (!isUserLoggedIn) {
        router.push({ name: "Login" });
        return;
      }

      userName.value = localStorage.getItem("username") || "";
      userRole.value = localStorage.getItem("role") || "";
    };

    const signout = () => {
      localStorage.clear();
      router.push({ name: "Login" });
    };

    onMounted(() => {
      checkSession();
    });

    return { signout, userRole, userName };
  },
};
</script>

<style scoped>
.border-bottom-1 {
  border-bottom: 1px solid #dee2e6;
}
</style>
