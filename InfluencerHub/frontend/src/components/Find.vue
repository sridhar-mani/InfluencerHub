<template>
  <div
    class="d-flex flex-column align-items-center w-100 justify-content-center"
  >
    <div>
      <BNavForm class="d-flex mt-3">
        <BFormInput
          class="me-2"
          v-model="searchQuery"
          placeholder="Search"
          @input="filterContent"
        />
        <BButton type="button" variant="outline-success">Filter</BButton>
      </BNavForm>
    </div>

    <BListGroup v-if="role === 'admin'" class="w-75 mt-2 mb-1 d-flex">
      <BListGroupItem
        v-for="s in sponsors"
        :key="s.id"
        class="list-group-item mb-1 d-flex justify-content-between flex-wrap align-items-center"
      >
        {{ s.name }} | {{ s.budget }} | {{ s.no_of_campaigns }} |
        {{ s.industry }}
        <div>
          <BButton
            pill
            variant="outline-light"
            :to="{ name: 'Oneprofile', params: { username: s.username } }"
          >
            View
          </BButton>
          <BButton pill variant="outline-light" @onClick="handleFlag">
            Flag
          </BButton>
        </div>
      </BListGroupItem>
    </BListGroup>

    <BListGroup class="w-75 mt-2 mb-1 d-flex">
      <BListGroupItem
        v-for="c in filteredCampaigns"
        :key="c.id"
        href="#"
        class="list-group-item mb-1 d-flex justify-content-between flex-wrap align-items-center"
      >
        {{ c.name }} | {{ c.goals }} | ₹{{ c.budget }} | {{ c.niche }} |
        {{ c.visibility }}
        <div class="d-flex gap-2">
          <BButton
            pill
            variant="outline-primary"
            :to="{ name: 'OneCampaign', params: { username: c.name } }"
            >View</BButton
          >
          <BButton pill variant="outline-success" v-if="role === 'influencer'"
            >Request</BButton
          >
        </div>
      </BListGroupItem>
    </BListGroup>

    <BListGroup
      v-if="role === 'admin' || role === 'sponsor'"
      class="w-75 mt-2 mb-1 d-flex"
    >
      <BListGroupItem
        v-for="i in influencers"
        :key="i.id"
        href="#"
        class="list-group-item mb-1 d-flex justify-content-between flex-wrap align-items-center"
      >
        {{ i.name }} | {{ i.category }} | {{ i.reach }} | {{ i.niche }}
        <div class="d-flex gap-2">
          <BButton pill variant="outline-primary">View</BButton>
          <BButton
            pill
            variant="outline-success"
            v-if="role === 'sponsor'"
            @click="handleRequest(i, 'influencer')"
            >Request</BButton
          >
        </div>
      </BListGroupItem>
    </BListGroup>

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
          console.log(response.data);
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
.modal-content {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 20px;
}

.modal-header,
.modal-footer {
  border: none;
}

.modal-header .modal-title {
  font-weight: 600;
}

.form-label {
  font-weight: 500;
}

.b-button {
  min-width: 100px;
}
</style>
