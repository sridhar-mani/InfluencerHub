<template>
  <BNavbar
    toggleable="lg"
    variant="Light"
    v-b-color-mode="'dark'"
    class="border-bottom-1"
  >
    <BNavbarBrand href="#" v-if="userRole == 'admin'"
      >Admins's Dashboard</BNavbarBrand
    >
    <BNavbarBrand href="#" v-else-if="userRole == 'influencer'"
      >Influencer's Dashboard</BNavbarBrand
    >
    <BNavbarBrand href="#" v-else>Sponsor</BNavbarBrand>
    <BNavbarToggle target="nav-collapse" />
    <BCollapse id="nav-collapse" is-nav>
      <BNavbarNav>
        <BNavItem v-if="userRole === 'admin'" :to="{ name: 'Info' }"
          >Info</BNavItem
        >
        <BNavItem
          href="#"
          v-if="userRole === 'sponsor'"
          :to="{ name: 'Campaign' }"
          >Campaigns</BNavItem
        >
        <BNavItem href="#" v-if="userRole" :to="{ name: 'Find' }"
          >Find</BNavItem
        >
        <BNavItem href="#" v-if="userRole" :to="{ name: 'Stats' }"
          >Stats</BNavItem
        >
      </BNavbarNav>
      <!-- Right aligned nav items -->
      <BNavbarNav class="ms-auto mb-2 mb-lg-0">
        <BNavItemDropdown right>
          <!-- Using 'button-content' slot -->
          <template #button-content>
            <BAvatar rounded="circle" size="1.5em" class="mx-1" />
            <b>{{ userName }}</b>
          </template>
          <BDropdownItem href="#" v-if="userRole === 'influencer'"
            >Profile</BDropdownItem
          >
          <BDropdownItem href="#" @click="signout">Sign Out</BDropdownItem>
        </BNavItemDropdown>
      </BNavbarNav>
      <BNavForm class="d-flex">
        <BFormInput class="me-2" placeholder="Search" />
        <BButton type="submit" variant="outline-success">Search</BButton>
      </BNavForm>
    </BCollapse>
  </BNavbar>
</template>

<script>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

export default {
  name: "Navbar",
  setup() {
    const userRole = ref(null);
    const router = useRouter();
    const userName = ref("");
    const checkSession = () => {
      const isUserLoggedIn = localStorage.getItem("username") !== null;

      if (!isUserLoggedIn) {
        router.push({ name: "Login" });
      }

      if (localStorage.getItem("username")) {
        userName.value = localStorage.getItem("username");
        userRole.value = localStorage.getItem("role");
        console.log(userRole);
      }
    };

    const signout = () => {
      localStorage.removeItem("username");
      localStorage.removeItem("role");
      router.push({ name: "Login" });
    };

    onMounted(() => {
      checkSession();
    });

    return { signout, userRole, userName };
  },
};
</script>

<style></style>
