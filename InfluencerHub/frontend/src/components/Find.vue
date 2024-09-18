<template>
  <div class="container py-4">
    <div class="row justify-content-center mb-4">
      <div class="col-md-8">
        <BNavForm class="d-flex mb-3">
          <BFormInput
            class="me-2"
            v-model="searchQuery"
            placeholder="Search for campaigns, sponsors, or influencers"
            @input="filterContent"
            size="lg"
          />
          <BButton type="button" variant="outline-success" size="lg"
            >Filter</BButton
          >
        </BNavForm>
      </div>
    </div>

    <div class="row justify-content-center">
      <div v-if="role === 'admin' && sponsors.length > 0" class="col-md-8 mb-4">
        <h4>Sponsors</h4>
        <div
          v-for="s in sponsors"
          :key="s.id"
          class="card mb-3 shadow-sm animated-card"
        >
          <div class="card-header bg-light d-flex justify-content-between">
            <span>{{ s.name }}</span>
            <span class="badge bg-primary">Sponsor</span>
          </div>
          <div class="card-body">
            <div class="more-info">
              <p>Industry: {{ s.industry }}</p>
              <p>Budget: {{ s.budget }}</p>
              <p>Name: {{ s.name }}</p>
            </div>
          </div>
          <div class="card-footer text-end">
            <BButton
              pill
              variant="outline-info"
              :to="{ name: 'OneProfile', params: { username: s.username } }"
              class="me-2"
            >
              View
            </BButton>
            <BButton pill variant="outline-danger" @click="handleFlag">
              Flag
            </BButton>
          </div>
        </div>
      </div>

      <div v-if="filteredCampaigns.length > 0" class="col-md-8 mb-4">
        <h4>Campaigns</h4>
        <div
          v-for="c in filteredCampaigns"
          :key="c.id"
          class="card mb-3 shadow-sm animated-card"
        >
          <div class="card-header bg-light d-flex justify-content-between">
            <span>{{ c.name }}</span>
            <span class="badge bg-success">{{ c.visibility }}</span>
          </div>
          <div class="card-body">
            <p>Niche: {{ c.niche }}</p>

            <div class="more-info">
              <p>Goals: {{ c.goals }}</p>
              <p>Budget: ₹{{ c.budget }}</p>
            </div>
          </div>
          <div class="card-footer text-end">
            <BButton
              pill
              variant="outline-primary"
              :to="{ name: 'OneCampaign', params: { username: c.name } }"
              class="me-2"
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
        </div>
      </div>

      <div
        v-if="
          (role === 'admin' || role === 'sponsor') && influencers.length > 0
        "
        class="col-md-8 mb-4"
      >
        <h4>Influencers</h4>
        <div
          v-for="i in influencers"
          :key="i.id"
          class="card mb-3 shadow-sm animated-card"
        >
          <div class="card-header bg-light d-flex justify-content-between">
            <span>{{ i.name }}</span>
            <span class="badge bg-warning">Influencer</span>
          </div>
          <div class="card-body">
            <p>Category: {{ i.category }}</p>
            <div class="more-info">
              <p>Reach: {{ i.reach }}</p>
              <p>Niche: {{ i.niche }}</p>
            </div>
          </div>
          <div class="card-footer text-end">
            <BButton pill variant="outline-primary" class="me-2">
              View
            </BButton>
            <BButton
              pill
              variant="outline-success"
              v-if="role === 'sponsor'"
              @click="handleRequest(i, 'influencer')"
            >
              Request
            </BButton>
          </div>
        </div>
      </div>
    </div>

    <BModal
      id="modal-center"
      v-model="modal"
      hide-footer
      centered
      title="Influencer Request"
      size="lg"
    >
      <BContainer fluid>
        <BRow class="mb-3">
          <BCol md="3" class="text-end">Message:</BCol>
          <BCol md="9">
            <BFormTextarea
              v-model="message"
              placeholder="Enter your message"
              rows="3"
              class="w-100"
            />
          </BCol>
        </BRow>
        <BRow class="mb-3">
          <BCol md="3" class="text-end">Requirements:</BCol>
          <BCol md="9">
            <BFormInput
              v-model="requirements"
              placeholder="Enter requirements"
              class="w-100"
            />
          </BCol>
        </BRow>
        <BRow class="mb-3">
          <BCol md="3" class="text-end">Amount:</BCol>
          <BCol md="9">
            <BFormInput
              v-model="amount"
              type="number"
              placeholder="Enter amount"
              class="w-100"
            />
          </BCol>
        </BRow>
        <BRow class="mb-4">
          <BCol md="3" class="text-end">Select Campaign:</BCol>
          <BCol md="9">
            <BFormSelect
              v-model="campaignSelected"
              :options="campaignOptions"
              class="w-100"
            />
          </BCol>
        </BRow>
        <BRow>
          <BCol class="d-flex justify-content-center">
            <BButton
              variant="success"
              class="px-4"
              @click="submitRequest('influencer')"
            >
              Submit
            </BButton>
          </BCol>
        </BRow>
      </BContainer>
    </BModal>
  </div>
</template>

<script>
import { onMounted, ref, computed } from "vue";
import axios from "axios";

export default {
  name: "Find",
  setup() {
    const campaigns = ref([]);
    const role = ref(null);
    const influencers = ref([]);
    const searchQuery = ref("");
    const modal = ref(false);
    const influencer = ref("");
    const campaignOptions = ref([]);
    const campaignSelected = ref(null);
    const message = ref("");
    const requirements = ref("");
    const amount = ref(null);
    const sponsors = ref([]);

    const loadSession = async () => {
      const username = localStorage.getItem("username");
      const userRole = localStorage.getItem("role");

      if (!username) {
        router.push({ name: "Login" });
      }

      role.value = userRole;

      try {
        const response = await axios.get(
          `http://localhost:5000/campaigns/${username}`
        );
        if (userRole === "influencer") {
          campaigns.value = response.data.campaigns;
        } else if (userRole === "sponsor") {
          campaigns.value = response.data.campaigns;
          influencers.value = response.data.influencers;
        } else {
          campaigns.value = response.data.campaigns;
          influencers.value = response.data.influencers;
          sponsors.value = response.data.sponsors;
          console.log(sponsors);
        }
      } catch (error) {
        console.error("Error loading session data:", error);
      }
    };

    const filteredCampaigns = computed(() => {
      return campaigns.value.filter((campaign) =>
        campaign.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });
    console.log(filteredCampaigns);

    const handleRequest = async (influer, type) => {
      influencer.value = influer.id;
      modal.value = true;
      campaignOptions.value = campaigns.value.map((c) => ({
        text: c.name,
        value: c.id,
      }));
    };

    const submitRequest = async (type) => {
      console.log("Request submitted", type, influencer.value);
      try {
        const { data } = await axios.post(
          `http://localhost:5000/submit_request/${type}/${influencer.value}`,
          {
            campaign_id: campaignSelected.value,
            message: message.value,
            requirements: requirements.value,
            amount: amount.value,
          }
        );
        if (data.message.includes("success")) {
          modal.value = false;
        }
      } catch (error) {
        console.error("Error sending request:", error);
      }
    };

    onMounted(() => {
      loadSession();
    });

    return {
      campaigns,
      sponsors,
      role,
      influencers,
      searchQuery,
      filteredCampaigns,
      handleRequest,
      modal,
      campaignOptions,
      campaignSelected,
      message,
      requirements,
      amount,
      submitRequest,
    };
  },
};
</script>

<style scoped>
.animated-card {
  transition: transform 0.3s, box-shadow 0.3s;
}
.animated-card:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.more-info {
  display: none;
}

.animated-card:hover .more-info {
  display: block;
}

.more-info p {
  margin: 0;
  padding: 0;
  opacity: 0.9;
}
</style>
