<template>
  <div class="container py-4">
    <div v-if="userData" class="card mb-3 shadow-sm">
      <div class="row no-gutters">
        <div
          class="col-md-4 d-flex justify-content-center align-items-center text-center"
        >
          <img
            :src="base + '/' + userData.profile_pic || defaultProfilePic"
            class="profile-img my-3"
            alt="Profile Picture"
          />
        </div>
        <div class="col-md-8">
          <div class="card-body">
            <h3 class="card-title">{{ userData.name }}</h3>
            <p class="card-text">
              <strong>Username:</strong> {{ userData.username }}
            </p>
            <p class="card-text">
              <strong>Email:</strong> {{ userData.email }}
            </p>
            <p class="card-text"><strong>Role:</strong> {{ userData.role }}</p>

            <div v-if="userData.role === 'influencer'">
              <p class="card-text">
                <strong>Category:</strong> {{ userData.category }}
              </p>
              <p class="card-text">
                <strong>Niche:</strong> {{ userData.niche }}
              </p>
              <p class="card-text">
                <strong>Reach:</strong> {{ userData.reach }}
              </p>
            </div>
            <div v-else-if="userData.role === 'sponsor'">
              <p class="card-text">
                <strong>Company Name:</strong> {{ userData.company_name }}
              </p>
              <p class="card-text">
                <strong>Industry:</strong> {{ userData.industry }}
              </p>
              <p class="card-text">
                <strong>Budget:</strong> ₹{{ userData.budget }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-else class="text-center my-5">
      <BSpinner variant="primary"></BSpinner>
      <p>Loading profile...</p>
    </div>

    <!-- Flag Confirmation Modal -->
    <BModal
      id="flag-modal"
      v-model="showFlagModal"
      title="Flag User"
      @ok="confirmFlag"
      ok-title="Confirm"
      cancel-title="Cancel"
      centered
    >
      <div>
        <p>Are you sure you want to flag this user?</p>
        <BFormTextarea
          v-model="flagReason"
          placeholder="Enter the reason for flagging (optional)"
          rows="3"
        ></BFormTextarea>
      </div>
    </BModal>

    <!-- Request Modal -->
    <BModal
      id="request-modal"
      v-model="showRequestModal"
      title="Send Collaboration Request"
      @ok="sendRequest"
      ok-title="Send"
      cancel-title="Cancel"
      centered
      size="lg"
    >
      <div>
        <!-- Campaign Selection -->
        <BFormGroup label="Select Campaign" label-for="campaign-select">
          <BFormSelect
            id="campaign-select"
            v-model="selectedCampaignId"
            :options="campaignOptions"
            required
          ></BFormSelect>
        </BFormGroup>

        <!-- Influencer Search and Selection -->
        <BFormGroup label="Select Influencers" label-for="influencers">
          <BInputGroup>
            <BFormInput
              id="influencers"
              v-model="influencerQuery"
              @input="fetchSuggestions"
              @focus="fetchSuggestions"
              placeholder="Search influencers"
              autocomplete="off"
            ></BFormInput>
            <BInputGroupAppend>
              <BButton @click="fetchSuggestions" variant="primary"
                >Find</BButton
              >
            </BInputGroupAppend>
          </BInputGroup>
        </BFormGroup>

        <!-- Influencer Suggestions -->
        <div v-if="showSuggestions" class="mt-2">
          <div v-for="s in suggestions" :key="s">
            <label>
              <input
                type="checkbox"
                :value="s"
                @change="handleCheckboxChange"
                v-model="selectedSuggestion"
              />
              {{ s }}
            </label>
          </div>
        </div>

        <!-- Message Field -->
        <BFormGroup label="Message">
          <BFormTextarea
            v-model="requestMessage"
            placeholder="Enter your message"
            rows="3"
          ></BFormTextarea>
        </BFormGroup>

        <!-- Requirements Field -->
        <BFormGroup label="Requirements">
          <BFormTextarea
            v-model="requestRequirements"
            placeholder="Enter any requirements"
            rows="3"
          ></BFormTextarea>
        </BFormGroup>

        <BFormGroup label="Payment Amount">
          <BFormInput
            v-model="requestPaymentAmount"
            type="number"
            min="0"
            placeholder="Enter payment amount"
          ></BFormInput>
        </BFormGroup>
      </div>
    </BModal>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  BModal,
  BButton,
  BFormGroup,
  BFormInput,
  BFormTextarea,
  BFormSelect,
  BSpinner,
} from "bootstrap-vue-next";

export default {
  name: "OneProfile",
  components: {
    BModal,
    BButton,
    BFormGroup,
    BFormInput,
    BFormTextarea,
    BFormSelect,
    BSpinner,
  },
  setup() {
    const route = useRoute();
    const username = route.params.username;
    const userData = ref(null);
    const currentUserRole = ref(localStorage.getItem("role"));
    const currentUsername = ref(localStorage.getItem("username"));
    const defaultProfilePic = "/path/to/default/profile/pic.png";

    const showFlagModal = ref(false);
    const flagReason = ref("");

    const showRequestModal = ref(false);
    const requestMessage = ref("");
    const base = "http://localhost:5000";
    const requestRequirements = ref("");
    const requestPaymentAmount = ref("");
    const selectedCampaignId = ref(null);
    const campaignOptions = ref([]);
    const influencerQuery = ref("");
    const suggestions = ref([]);
    const showSuggestions = ref(false);

    const selectedSuggestion = ref([]);

    const handleRequest = () => {
      // Reset request form fields
      requestMessage.value = "";
      requestRequirements.value = "";
      requestPaymentAmount.value = "";
      selectedCampaignId.value = null;
      selectedSuggestion.value = [];
      influencerQuery.value = "";
      showSuggestions.value = false;
      showRequestModal.value = true; // Open the modal
    };
    const fetchSuggestions = async () => {
      const query = influencerQuery.value;
      if (query.length > 1) {
        try {
          const response = await axios.get(
            `http://localhost:5000/users/get_influencers`,
            {
              params: { query },
            }
          );
          suggestions.value = response.data;
          showSuggestions.value = true;
        } catch (error) {
          console.error("Error fetching suggestions:", error);
        }
      } else {
        showSuggestions.value = false;
      }
    };

    const loadUserProfile = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5000/users/${username}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        userData.value = response.data;

        if (
          currentUserRole.value === "sponsor" &&
          userData.value.role === "influencer"
        ) {
          await loadCampaigns();
        }
      } catch (error) {
        console.error("Error loading user profile:", error);
      }
    };

    const loadCampaigns = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5000/campaigns/${currentUsername.value}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        const campaigns = response.data.campaigns;
        campaignOptions.value = campaigns.map((campaign) => ({
          value: campaign.id,
          text: campaign.name,
        }));
      } catch (error) {
        console.error("Error loading campaigns:", error);
      }
    };

    // Handle flagging
    const handleFlag = () => {
      flagReason.value = "";
      showFlagModal.value = true;
    };

    const confirmFlag = async () => {
      try {
        const data = {
          flag_reason: flagReason.value,
        };
        const response = await axios.post(
          `http://localhost:5000/flaguser/${username}`,
          data,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        alert(response.data.message);
      } catch (error) {
        console.error("Error flagging user:", error);
        alert("Failed to flag user.");
      } finally {
        showFlagModal.value = false;
      }
    };

    const sendRequest = async () => {
      if (!selectedCampaignId.value) {
        alert("Please select a campaign.");
        return;
      }
      try {
        const data = {
          message: requestMessage.value,
          requirements: requestRequirements.value,
          payment_amount: requestPaymentAmount.value,
          influencers: userData.value.name,
        };

        const response = await axios.post(
          `http://localhost:5000/add_adrequest/${currentUsername.value}/${selectedCampaignId.value}`,
          data,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        alert(response.data.message);
      } catch (error) {
        console.error("Error sending request:", error);
        alert("Failed to send request.");
      } finally {
        showRequestModal.value = false;
      }
    };

    onMounted(() => {
      loadUserProfile();
    });

    return {
      userData,
      currentUserRole,
      defaultProfilePic,
      showFlagModal,
      flagReason,
      handleFlag,
      confirmFlag,
      showRequestModal,
      requestMessage,
      requestRequirements,
      requestPaymentAmount,
      selectedCampaignId,
      campaignOptions,
      sendRequest,
      base,
      handleRequest,
      fetchSuggestions,
    };
  },
};
</script>

<style scoped>
.profile-img {
  width: 200px;
  height: 200px;
  object-fit: cover;
  border-radius: 50%;
}

.card-body {
  padding: 20px;
}

.card-text {
  margin-bottom: 10px;
}

.text-end {
  margin-top: 20px;
}

.card-title {
  font-weight: bold;
}

@media (max-width: 768px) {
  .profile-img {
    width: 150px;
    height: 150px;
  }
}
</style>
