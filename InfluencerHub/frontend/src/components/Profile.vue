<template>
  <BContainer fluid class="p-3 d-flex w-100 justify-content-center">
    <BContainer fluid class="p-3 w-75">
      <BRow class="mt-3">
        <!-- Influencer's profile section -->
        <BCol md="3" v-if="role === 'influencer'">
          <BCard class="profile-card w-100 text-center">
            <div class="profile-img-wrapper">
              <BImg
                :src="
                  mainProps.src
                    ? mainProps.src
                    : base + 'profile_pics/blank-profile-picture-973460_640.png'
                "
                class="profile-img"
                rounded
                alt="Profile picture"
              />
            </div>
            <div class="profile-info">
              <h5 class="fw-bold">{{ username }}</h5>
              <p class="text-muted">
                {{ role === "influencer" ? "Influencer" : "Sponsor" }}
              </p>
              <BCardText
                class="d-flex justify-content-between mb-0 align-items-center"
              >
                <p class="fw-bold">Earnings (This Month):</p>
                <p>₹{{ user?.earnings || 0 }}</p>
              </BCardText>
              <BCardText
                class="d-flex justify-content-between align-items-center gap-2"
              >
                <p class="fw-bold">Reach:</p>
                <p v-if="reach">{{ reach }}</p>
              </BCardText>
            </div>
          </BCard>
        </BCol>

        <!-- Campaign and Ad Request Section -->
        <BCol md="9">
          <h2 class="text-primary mb-4">Welcome {{ username }}</h2>

          <!-- Active Campaigns -->
          <div v-if="campaigns.length > 0" class="mb-4">
            <h3 class="mt-4 text-success">Active Campaigns:</h3>
            <BListGroup
              class="w-100 mt-2 mb-1 d-flex"
              v-for="c in campaigns"
              :key="c.id"
            >
              <BListGroupItem
                href="#"
                class="list-group-item mb-1 p-3 d-flex justify-content-between align-items-center"
                :to="{ name: `OneCampaign`, params: { username: c.name } }"
              >
                <div>
                  <strong>{{ c.name }}</strong> <br />
                  <small
                    >{{ c.goals }} | ₹{{ c.budget }} | {{ c.niche }} |
                    {{ c.visibility }}</small
                  >
                </div>
                <div class="d-flex gap-2">
                  <BButton
                    pill
                    variant="outline-primary"
                    :to="{
                      name: `OneCampaign`,
                      params: { username: c.name, name: username },
                    }"
                  >
                    View
                  </BButton>
                  <BButton
                    pill
                    variant="outline-success"
                    v-if="role === 'influencer'"
                  >
                    Request
                  </BButton>
                </div>
              </BListGroupItem>
            </BListGroup>
          </div>

          <!-- New Ad Requests -->
          <h3 class="mt-4 text-warning">New Requests:</h3>
          <BListGroup class="mb-4">
            <BListGroupItem
              class="d-flex justify-content-between align-items-center"
              v-for="request in campaignad"
              :key="request.id"
            >
              {{ request.campaign_name }} | ₹{{ request.payment_amount }}
              <div class="d-flex justify-content-evenly w-50">
                <BButton
                  variant="warning"
                  size="sm w-25"
                  @click="openModal(request)"
                >
                  View
                </BButton>
                <BButton
                  variant="success"
                  size="sm w-25"
                  @click="acceptRequest(request)"
                >
                  Accept
                </BButton>
                <BButton
                  variant="danger"
                  size="sm w-25"
                  @click="rejectRequest(request)"
                >
                  Reject
                </BButton>
              </div>
            </BListGroupItem>
          </BListGroup>
        </BCol>
      </BRow>

      <!-- Modal for Ad Request Details -->
      <BModal
        v-model="showModal"
        title="Ad Request Details"
        hide-footer
        centered
      >
        <div v-if="selectedRequest">
          <p>
            <strong>Campaign Name:</strong> {{ selectedRequest.campaign_name }}
          </p>
          <p><strong>Message:</strong> {{ selectedRequest.message }}</p>
          <p>
            <strong>Requirements:</strong> {{ selectedRequest.requirements }}
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
    const reach = ref("0");

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

    const loadSession = async () => {
      try {
        role.value = localStorage.getItem("role");
        username.value = localStorage.getItem("username");
        if (!role.value || !username.value) {
          router.push({ name: "Login" });
          return;
        }

        const campaignResponse = await axios.get(
          `http://localhost:5000/campaigns/${username.value}`
        );
        campaigns.value = campaignResponse.data.campaigns;

        // Fetch ad requests
        const campaignAdResponse = await axios.get(
          `http://localhost:5000/adrequests/${username.value}`
        );
        campaignad.value = campaignAdResponse.data;

        // Fetch user data
        const userResponse = await axios.get(
          `http://localhost:5000/users/${username.value}`
        );
        user.value = userResponse.data;

        reach.value = user.value.reach;

        // If user is an influencer, load profile picture
        if (role.value === "influencer" && userResponse.data.profile_pic) {
          mainProps.value.src = `${import.meta.env.VITE_APP_API_BASE_URL}/${
            userResponse.data.profile_pic
          }`;
        }
      } catch (error) {
        console.error("Error loading session:", error);
      }
    };

    onMounted(() => {
      loadSession();
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
      user,
      reach,
    };
  },
};
</script>
<style scoped>
.profile-card {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
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

.profile-info h5 {
  margin-top: 10px;
  font-weight: bold;
}

.b-list-group-item {
  padding: 20px;
  margin-bottom: 10px;
}

.b-button {
  margin-right: 10px;
}

.d-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .profile-card {
    margin-bottom: 20px;
  }

  .profile-img {
    width: 80px;
    height: 80px;
  }

  .b-list-group-item {
    padding: 10px;
  }
}
</style>
