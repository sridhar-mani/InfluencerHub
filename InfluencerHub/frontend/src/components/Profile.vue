<template>
  <BContainer fluid class="p-3 d-flex w-100 justify-content-center">
    <BContainer fluid class="p-3 w-75">
      <BRow class="mt-3">
        <BCol md="3" v-if="role === 'influencer'">
          <BModal
            v-model="showModal"
            title="Ad Request Details"
            hide-footer
            centered
          >
            <div v-if="selectedRequest">
              <p>
                <strong>Campaign Name:</strong>
                {{ selectedRequest.campaign_name }}
              </p>
              <p><strong>Message:</strong> {{ selectedRequest.message }}</p>
              <p>
                <strong>Requirements:</strong>
                {{ selectedRequest.requirements }}
              </p>
              <p>
                <strong>Payment Amount:</strong> ₹{{
                  selectedRequest.payment_amount
                }}
              </p>
            </div>
            <BButton
              variant="success"
              class="w-100 mt-3"
              @click="acceptRequest(selectedRequest)"
            >
              Accept
            </BButton>
            <BButton
              variant="danger"
              class="w-100 mt-2"
              @click="rejectRequest(selectedRequest)"
            >
              Reject
            </BButton>
          </BModal>
          <BCard class="profile-card w-75">
            <div class="profile-img-wrapper">
              <BImg
                :src="mainProps.src"
                class="profile-img"
                rounded
                alt="Profile picture"
              />
            </div>
            <div class="profile-info d-flex align-items-start">
              <BCardText
                class="profile-rating w-100 d-flex justify-content-between align-items-center"
                ><p>Rating:</p>
                <p style="font-size: 13px">{{ displayStars }}</p></BCardText
              >

              <BCardText
                class="profile-earnings d-flex justify-content-between align-items-center gap-2"
              >
                <p class="fw-bold text-start w-auto">Earnings (This Month):</p>
                <p>$500</p>
              </BCardText>
            </div>
          </BCard>
        </BCol>

        <BCol md="9">
          <h2>Welcome {{ username }}</h2>

          <h3 class="mt-4">Active Campaigns:</h3>
          <BListGroup
            class="w-100 mt-2 mb-1 d-flex"
            v-for="c in campaigns"
            :key="c.id"
          >
            <BListGroupItem
              href="#"
              class="list-group-item mb-1 d-flex justify-content-between flex--wrap align-items-center"
              :to="{ name: `OneCampaign`, params: { username: c.name } }"
              >{{ c.name }} | {{ c.goals }} | ₹{{ c.budget }} | {{ c.niche }} |
              {{ c.visibility }}
              <div class="d-flex gap-2">
                <BButton
                  pill
                  variant="outline-primary"
                  :to="{ name: `OneCampaign`, params: { username: c.name } }"
                  >View</BButton
                >
                <BButton
                  pill
                  variant="outline-success"
                  v-if="role === 'influencer'"
                  >Request</BButton
                >
              </div></BListGroupItem
            >
          </BListGroup>

          <h3 class="mt-4">New Requests:</h3>
          <BListGroup>
            <BListGroupItem
              class="d-flex justify-content-between align-items-center"
              v-for="request in campaignad"
              :key="request.id"
            >
              {{ request.campaign_name }} | ₹{{ request.payment_amount }}
              <div class="w-50 d-flex justify-content-evenly">
                <BButton
                  variant="warning"
                  size="sm w-25"
                  @click="openModal(request)"
                  >view</BButton
                >
                <BButton
                  variant="success"
                  size="sm w-25"
                  @click="acceptRequest(request)"
                  >accept</BButton
                >
                <BButton
                  variant="danger"
                  size="sm w-25"
                  @click="rejectRequest(request)"
                  >reject</BButton
                >
              </div>
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
    const campaigns = ref([]);
    const mainProps = ref({
      src: "",
      alt: "image",
    });
    const rating = ref(5);
    const showModal = ref(false);
    const selectedRequest = ref(null);
    const campaignad = ref([]);
    const displayStars = computed(() => "⭐️".repeat(rating.value));

    const openModal = (request) => {
      selectedRequest.value = request;
      showModal.value = true;
    };
    const acceptRequest = async (request) => {
      try {
        await axios.post(
          `http://localhost:5000/process_request/${request.id}`,
          {
            sender: role.value,
            todo: "accept",
          }
        );
        showModal.value = false;
      } catch (error) {
        console.error("Error accepting request:", error);
      }
    };

    const rejectRequest = async (request) => {
      try {
        await axios.post(`http://localhost:5000/process_request/${request.id}`),
          {
            todo: "reject",
          };
        showModal.value = false;
      } catch (error) {
        console.error("Error rejecting request:", error);
      }
    };

    onMounted(async () => {
      role.value = localStorage.getItem("role");
      username.value = localStorage.getItem("username");
      const response = await axios.get(
        `http://localhost:5000/campaigns/${localStorage.getItem("username")}`
      );
      campaigns.value = response.data.campaigns;
      const campaignRes = await axios.get(
        `http://localhost:5000/adrequests/${localStorage.getItem("username")}`
      );
      campaignad.value = campaignRes.data;
      user.value = response.data;
      if (!role.value) {
        router.push({ name: "Login" });
      }
      const { data } = await axios.get(
        `http://localhost:5000/users/${localStorage.getItem("username")}`
      );
      if (role.value === "influencer") {
        const userResponse = await axios.get(
          `http://localhost:5000/users/${username.value}`
        );
        console.log(userResponse.data);
        mainProps.value.src = `${import.meta.env.VITE_APP_API_BASE_URL}/${
          userResponse.data.profile_pic
        }`;
      }
    });

    return {
      username,
      role,
      mainProps,
      rating,
      displayStars,
      campaigns,
      campaignad,
      openModal,
      showModal,
      selectedRequest,
      acceptRequest,
      rejectRequest,
    };
  },
};
</script>

<style scoped>
.profile-card {
  background-color: #ffffff;

  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.profile-img-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.profile-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-rating {
  font-size: 1.2em;
  font-weight: bold;
  color: #333;
}

.profile-earnings {
  font-size: 1em;
  color: #666;
}

.b-form-checkbox input[type="checkbox"]:focus {
  box-shadow: none;
  outline: none;
}
</style>
