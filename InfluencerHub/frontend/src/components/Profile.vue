<template>
  <BContainer fluid class="p-3 d-flex w-100 justify-content-center">
    <BContainer fluid class="p-3 w-75">
      <BRow class="mt-3">
        <BCol md="3" v-if="role === 'influencer'">
          <BCard class="text-center">
            <BImg
              :src="mainProps.src"
              class="w-100 h-100"
              rounded
              alt="Rounded image"
            />
            <BCardText class="w-100 d-flex align-items-lg-start mt-1 mb-0"
              >Rating:{{ displayStars }}</BCardText
            >
            <BCardText class="w-100 d-flex align-items-lg-start mt-1 mb-0"
              >Earnings(This Month): $ 500</BCardText
            >
          </BCard>
        </BCol>

        <BCol md="9">
          <h2>Welcome {{ username }}</h2>

          <h3 class="mt-4">Active Campaigns:</h3>
          <BListGroup>
            <BListGroupItem
              class="d-flex justify-content-between align-items-center"
              v-for="campaign in activeCampaigns"
              :key="campaign.id"
            >
              {{ campaign.name }} | Progress {{ campaign.progress }}%
              <BButton variant="warning" size="sm">view</BButton>
            </BListGroupItem>
          </BListGroup>

          <h3 class="mt-4">New Requests:</h3>
          <BListGroup>
            <BListGroupItem
              class="d-flex justify-content-between align-items-center"
              v-for="request in newRequests"
              :key="request.id"
            >
              {{ request.name }} | {{ request.company }}
              <BButtonGroup>
                <BButton variant="warning" size="sm">view</BButton>
                <BButton variant="success" size="sm">accept</BButton>
                <BButton variant="danger" size="sm">reject</BButton>
              </BButtonGroup>
            </BListGroupItem>
          </BListGroup>
        </BCol>
      </BRow>
    </BContainer>
  </BContainer>
</template>

<script>
import axios from "axios";
import { ref, onMounted, computed } from "vue";

export default {
  name: "Profile",
  setup() {
    const role = ref(null);
    const username = ref(null);
    const user = ref(null);
    const mainProps = ref({
      src: "",
      alt: "image",
    });
    const rating = ref(2);
    const displayStars = computed(() => "⭐️".repeat(rating.value));

    onMounted(async () => {
      role.value = localStorage.getItem("role");
      username.value = localStorage.getItem("username");
      const response = await axios.get(
        `http://localhost:5000/users/${username.value}`
      );
      user.value = response.data; // Assign fetched data to user
      console.log(user);
      if (!role.value) {
        router.push({ name: "Login" });
      }
      if (role.value === "influencer") {
        mainProps.value.src = user.value.profile_pic;
        console.log(import.meta.env);
        mainProps.value.src = `${
          import.meta.env.VITE_APP_API_BASE_URL
        }/`.concat(mainProps.value.src);
      }
    });

    return { username, role, mainProps, rating, displayStars };
  },
};
</script>

<style></style>
