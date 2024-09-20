<template>
  <div class="container mt-0 w-100">
    <b-card class="mb-1 mt-2">
      <template #header>
        <b-card-title>{{ campaign.name }}</b-card-title>
        <b-card-sub-title class="text-muted">
          <span>Start Date: {{ campaign.start_date }}</span> |
          <span>End Date: {{ campaign.end_date }}</span>
        </b-card-sub-title>
      </template>

      <b-card-img
        :src="campaignimg"
        alt="Campaign Image"
        class="mb-2"
        style="height: 300px; width: 300px; maxwidth: 100%"
      ></b-card-img>

      <b-card-text class="mb-0">
        <b-row>
          <b-col>
            <p class="mb-2">
              <strong>Description:</strong> {{ campaign.description }}
            </p>
            <p class="mb-2"><strong>Budget:</strong> ${{ campaign.budget }}</p>
            <p class="mb-2">
              <strong>Visibility:</strong> {{ campaign.visibility }}
            </p>
            <p class="mb-2"><strong>Goals:</strong> {{ campaign.goals }}</p>
            <p class="mb-0"><strong>Niche:</strong> {{ campaign.niche }}</p>
          </b-col>

          <b-col class="d-flex justify-content-end align-items-end">
            <b-button
              @click="openModal"
              variant="success"
              v-if="userRole === 'sponsor'"
              style="
                font-size: 30px;
                width: 70px;
                height: 70px;
                display: flex;
                justify-content: center;
                align-items: center;
                border-radius: 50%;
              "
              >+</b-button
            >
          </b-col>
        </b-row>
      </b-card-text>
      <!-- Modal for Adding or Editing Ad Request -->
      <BModal
        id="modal-center"
        v-model="modal"
        hide-footer
        centered
        title="Add or Edit Ad Request"
      >
        <BForm @submit.prevent="submitAdRequest" v-if="userRole === 'sponsor'">
          <BFormGroup label="Message:" label-for="message">
            <BFormTextarea
              id="message"
              v-model="adRequest.message"
              required
            ></BFormTextarea>
          </BFormGroup>
          <BFormGroup label="Requirements:" label-for="requirements">
            <BFormInput
              id="requirements"
              v-model="adRequest.requirements"
              required
            ></BFormInput>
          </BFormGroup>
          <BFormGroup
            label="Proposed Payment Amount:"
            label-for="payment-amount"
          >
            <BFormInput
              id="payment-amount"
              v-model.number="adRequest.payment_amount"
              type="number"
              required
            ></BFormInput>
          </BFormGroup>
          <BFormGroup label="Influencers:" label-for="influencers">
            <BInputGroup>
              <BFormInput
                id="influencers"
                v-model="influencerQuery"
                @input="fetchSuggestions"
                @focus="fetchSuggestions"
                autocomplete="off"
              ></BFormInput>
              <BButton @click="fetchSuggestions" variant="primary"
                >Find</BButton
              >
            </BInputGroup>
          </BFormGroup>

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

          <div class="w-100 d-flex justify-content-center mt-3">
            <div class="w-100 d-flex justify-content-center mt-3">
              <BButton
                type="submit"
                variant="success"
                :disabled="selectedSuggestion.length === 0"
              >
                Submit Ad Request
              </BButton>
            </div>
          </div>
        </BForm>
      </BModal>
    </b-card>
    <div class="w-100 d-flex justify-content-between">
      <b-button variant="primary" @click="goBack">Go Back</b-button>
      <b-button
        variant="success"
        v-if="userRole === 'sponsor'"
        @click="handleDldstats(campaign.id)"
        :disabled="isDownloading"
      >
        {{ isDownloading ? "Downloading..." : "Download Campaign Statistics" }}
      </b-button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute } from "vue-router";
import { BContainer, BRow, BToast } from "bootstrap-vue-next";
import router from "../routes";

export default {
  name: "OneCampaign",
  components: { BContainer, BRow, BToast },
  setup() {
    const route = useRoute();
    const campaignimg = ref("");
    const campaign = ref({});
    const modal = ref(false);
    const isDownloading = ref(false);
    const selectedSuggestion = ref([]); // Should be an empty array
    const selectedInfluencers = ref([]);
    const userRole = ref(localStorage.getItem("role") || "");
    const adRequest = ref({
      name: "",
      message: "",
      requirements: "",
      payment_amount: 0,
      influencers: [],
    });
    const influencerQuery = ref("");
    const suggestions = ref([]);
    const showSuggestions = ref(false);

    const openModal = () => {
      modal.value = !modal.value;
    };

    const goBack = () => {
      router.go(-1);
    };

    const handleCheckboxChange = (event) => {
      const value = event.target.value;
      const checked = event.target.checked;
      if (checked) {
        if (!selectedSuggestion.value.includes(value)) {
          selectedSuggestion.value.push(value);
        }
      } else {
        selectedSuggestion.value = selectedSuggestion.value.filter(
          (s) => s !== value
        );
      }
    };

    const handleDldstats = async (id) => {
      try {
        isDownloading.value = true; // Start the loading state
        const response = await axios.get(
          `http://localhost:5000/download_campaign/${id}/${username}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        alert("Download initiated successfully");
      } catch (error) {
        console.error("Error downloading campaign stats:", error);
        alert("Failed to initiate download");
      } finally {
        isDownloading.value = false; // End the loading state
      }
    };

    const loadCampaign = async () => {
      try {
        const username = route.params.username;
        const campaignName = route.params.name;
        console.log(username, campaignName);

        // Replace this with your actual backend URL
        const baseUrl = import.meta.env.VITE_APP_API_BASE_URL;

        const response = await axios.get(
          `http://localhost:5000/campaign/${username}/${campaignName}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );

        if (response.data && response.data.length > 0) {
          campaign.value = response.data[0];
          campaignimg.value = `http://localhost:5000/${campaign.value.campaign_pic}`;
        } else {
          console.error("No campaigns found");
        }
      } catch (error) {
        console.error(
          "Error loading campaign:",
          error.response ? error.response.data : error.message
        );
      }
    };

    const submitAdRequest = async () => {
      if (selectedSuggestion.value.length === 0) {
        alert("Please select at least one influencer.");
        return;
      }
      try {
        adRequest.value.influencers = selectedSuggestion.value;
        const method = adRequest.value.id ? "put" : "post";
        const url = adRequest.value.id
          ? `http://localhost:5000/add_adrequest/${localStorage.getItem(
              "username"
            )}/${campaign.value.id}/${adRequest.value.id}`
          : `http://localhost:5000/add_adrequest/${localStorage.getItem(
              "username"
            )}/${campaign.value.id}`;

        const response = await axios({
          method,
          url,
          data: adRequest.value,
        });

        console.log(response);
        adRequest.value = {
          message: "",
          requirements: "",
          payment_amount: 0,
          influencers: [],
        };
        selectedSuggestion.value = [];
        modal.value = false;
        alert("Ad request submitted successfully");
      } catch (error) {
        console.error("Error submitting ad request:", error);
        alert("Failed to submit ad request");
      }
    };

    const fetchSuggestions = async () => {
      const query = influencerQuery.value;
      if (query.length > 0) {
        try {
          const response = await axios.get(
            `http://localhost:5000/users/get_influencers`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
              },
              params: { query },
            }
          );
          suggestions.value = response.data;
          showSuggestions.value = true;

          console.log(suggestions.value);
        } catch (error) {
          console.error("Error fetching suggestions:", error);
        }
      } else {
        showSuggestions.value = false;
      }
    };

    onMounted(() => {
      loadCampaign();
    });

    return {
      campaign,
      campaignimg,
      modal,
      userRole,
      adRequest,
      suggestions,
      showSuggestions,
      influencerQuery,
      selectedInfluencers,
      selectedSuggestion,
      openModal,
      submitAdRequest,
      handleDldstats,
      fetchSuggestions,
      goBack,
    };
  },
};
</script>

<style scoped></style>
