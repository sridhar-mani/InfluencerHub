<template>
  <div class="container py-4">
    <!-- Search Bar -->
    <div class="row justify-content-center mb-4">
      <div class="col-md-8">
        <b-nav-form class="d-flex mb-3">
          <b-form-input
            class="me-2"
            v-model="searchQuery"
            placeholder="Enter your search here"
            size="lg"
          />
          <b-button
            type="button"
            variant="outline-success"
            size="lg"
            @click="filterContent"
          >
            Find
          </b-button>
        </b-nav-form>
      </div>
    </div>

    <!-- Display Filtered Content -->
    <div class="row justify-content-center">
      <!-- Display Sponsors -->
      <div v-if="filteredContent.sponsors.length > 0" class="col-md-8 mb-4">
        <h4>Sponsors</h4>
        <div
          v-for="s in filteredContent.sponsors"
          :key="s.id"
          class="card mb-3 shadow-sm animated-card"
        >
          <div class="card-header bg-light d-flex justify-content-between">
            <span>{{ s.name }}</span>
            <span class="badge bg-primary">Sponsor</span>
          </div>
          <div class="card-body">
            <p>Company: {{ s.company_name }}</p>
            <p>Industry: {{ s.industry }}</p>
            <p>Budget: ₹{{ s.budget }}</p>
          </div>
          <div class="card-footer text-end">
            <b-button
              pill
              variant="outline-info"
              :to="{ name: 'OneProfile', params: { username: s.username } }"
              class="me-2"
            >
              View
            </b-button>
            <!-- Flag Button for Admin -->
            <b-button
              pill
              variant="outline-danger"
              v-if="role === 'admin'"
              @click="handleFlag(s, 'sponsor')"
            >
              Flag
            </b-button>
          </div>
        </div>
      </div>

      <!-- Display Campaigns -->
      <div v-if="filteredContent.campaigns.length > 0" class="col-md-8 mb-4">
        <h4>Campaigns</h4>
        <div
          v-for="c in filteredContent.campaigns"
          :key="c.id"
          class="card mb-3 shadow-sm animated-card"
        >
          <div class="card-header bg-light d-flex justify-content-between">
            <span>{{ c.name }}</span>
            <span class="badge bg-success">{{ c.visibility }}</span>
          </div>
          <div class="card-body">
            <p>Niche: {{ c.niche }}</p>
            <p>Goals: {{ c.goals }}</p>
            <p>Budget: ₹{{ c.budget }}</p>
          </div>
          <div class="card-footer text-end">
            <b-button
              pill
              variant="outline-primary"
              :to="{
                name: 'OneCampaign',
                params: { username: c.name, name: usersname },
              }"
              class="me-2"
            >
              View
            </b-button>
            <!-- Flag Button for Admin -->
            <b-button
              pill
              variant="outline-danger"
              v-if="role === 'admin'"
              @click="handleFlag(c, 'campaign')"
              class="me-2"
            >
              Flag
            </b-button>
            <b-button
              pill
              variant="outline-success"
              v-if="role === 'influencer'"
            >
              Request
            </b-button>
          </div>
        </div>
      </div>

      <div v-if="filteredContent.influencers.length > 0" class="col-md-8 mb-4">
        <h4>Influencers</h4>
        <div
          v-for="i in filteredContent.influencers"
          :key="i.id"
          class="card mb-3 shadow-sm animated-card"
        >
          <div class="card-header bg-light d-flex justify-content-between">
            <span>{{ i.name }}</span>
            <span class="badge bg-warning">Influencer</span>
          </div>
          <div class="card-body">
            <p>Category: {{ i.category }}</p>
            <p>Reach: {{ i.reach }}</p>
            <p>Niche: {{ i.niche }}</p>
          </div>
          <div class="card-footer text-end">
            <b-button
              pill
              variant="outline-primary"
              :to="{ name: 'OneProfile', params: { username: i.username } }"
              class="me-2"
            >
              View
            </b-button>
            <b-button
              pill
              variant="outline-danger"
              v-if="role === 'admin'"
              @click="handleFlag(i, 'influencer')"
              class="me-2"
            >
              Flag
            </b-button>
            <BButton
              pill
              variant="outline-success"
              v-if="role === 'sponsor'"
              @click="openModal(i)"
            >
              Request
            </BButton>
          </div>
        </div>
      </div>
    </div>

    <b-modal
      id="flag-modal"
      v-model="showFlagModal"
      title="Flag Item"
      @ok="confirmFlag"
      ok-title="Confirm"
      cancel-title="Cancel"
      centered
    >
      <div>
        <p>Are you sure you want to flag this {{ flagItemType }}?</p>
        <b-form-textarea
          v-model="flagReason"
          placeholder="Enter the reason for flagging (optional)"
          rows="3"
        ></b-form-textarea>
      </div>
    </b-modal>
    <b-modal
      id="modal-center"
      v-model="modal"
      hide-footer
      centered
      title="Add or Edit Ad Request"
    >
      <b-form @submit.prevent="submitAdRequest" v-if="role === 'sponsor'">
        <b-form-group label="Message:" label-for="message">
          <b-form-textarea
            id="message"
            v-model="adRequest.message"
            required
          ></b-form-textarea>
        </b-form-group>
        <b-form-group label="Requirements:" label-for="requirements">
          <b-form-input
            id="requirements"
            v-model="adRequest.requirements"
            required
          ></b-form-input>
        </b-form-group>
        <b-form-group
          label="Proposed Payment Amount:"
          label-for="payment-amount"
        >
          <b-form-input
            id="payment-amount"
            v-model.number="adRequest.payment_amount"
            type="number"
            required
          ></b-form-input>
        </b-form-group>

        <div class="w-100 d-flex justify-content-center mt-3">
          <b-button type="submit" variant="success">
            Submit Ad Request
          </b-button>
        </div>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  name: "Find",
  setup() {
    const router = useRouter();
    const campaigns = ref([]);
    const influencers = ref([]);
    const sponsors = ref([]);
    const searchQuery = ref("");
    const modal = ref(false);
    const role = ref(null);
    const usersname = ref("");
    const showFlagModal = ref(false);
    const flagItem = ref(null);
    const flagItemType = ref("");
    const flagReason = ref("");

    const loadSession = async () => {
      const username = localStorage.getItem("username");
      const userRole = localStorage.getItem("role");
      usersname.value = username;

      if (!username) {
        router.push({ name: "Login" });
      }

      role.value = userRole;

      try {
        const response = await axios.get(
          `http://localhost:5000/campaigns/${username}`
        );
        console.log(response);
        campaigns.value = response.data.campaigns;
        if (userRole === "sponsor" || userRole === "admin") {
          influencers.value = response.data.influencers;
        }
        if (userRole === "admin") {
          sponsors.value = response.data.sponsors;
        }
      } catch (error) {
        console.error("Error loading session data:", error);
      }
    };

    const filteredContent = computed(() => {
      const query = searchQuery.value.toLowerCase();
      return {
        campaigns: campaigns.value.filter(
          (c) =>
            c.name.toLowerCase().includes(query) ||
            c.niche.toLowerCase().includes(query) ||
            (c.goals && c.goals.toLowerCase().includes(query)) ||
            (c.budget && c.budget.toString().includes(query))
        ),
        influencers: influencers.value.filter(
          (i) =>
            i.name.toLowerCase().includes(query) ||
            (i.category && i.category.toLowerCase().includes(query)) ||
            (i.reach && i.reach.toString().includes(query)) ||
            (i.niche && i.niche.toLowerCase().includes(query))
        ),
        sponsors: sponsors.value.filter(
          (s) =>
            s.name.toLowerCase().includes(query) ||
            (s.company_name && s.company_name.toLowerCase().includes(query)) ||
            (s.industry && s.industry.toLowerCase().includes(query)) ||
            (s.budget && s.budget.toString().includes(query))
        ),
      };
    });

    // Handle Flagging
    const handleFlag = (item, itemType) => {
      flagItem.value = item;
      flagItemType.value = itemType;
      flagReason.value = "";
      showFlagModal.value = true;
    };

    const confirmFlag = async () => {
      try {
        let endpoint = "";
        const data = {
          flag_reason: flagReason.value,
        };

        if (
          flagItemType.value === "sponsor" ||
          flagItemType.value === "influencer"
        ) {
          endpoint = `http://localhost:5000/flaguser/${flagItem.value.username}`;
        } else if (flagItemType.value === "campaign") {
          endpoint = `http://localhost:5000/flagcampaign/${flagItem.value.id}`;
        }

        const response = await axios.post(endpoint, data, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        alert(response.data.message);
      } catch (error) {
        console.error("Error flagging item:", error);
        alert("Failed to flag item.");
      } finally {
        showFlagModal.value = false;
      }
    };

    const handleRequest = async (influencer) => {
      try {
        const campaignId = prompt("Enter the campaign ID for the ad request:");
        const paymentAmount = prompt(
          "Enter the payment amount for the ad request:"
        );
        const message = prompt("Enter the message for the ad request:");

        if (!campaignId || !paymentAmount || isNaN(paymentAmount)) {
          alert("Please enter valid values.");
          return;
        }

        const data = {
          message,
          payment_amount: paymentAmount,
          requirements: "Please review the campaign.",
          influencers: influencer.name,
        };

        const response = await axios.post(
          `http://localhost:5000/add_adrequest/${localStorage.getItem(
            "username"
          )}/${campaignId}`,
          data,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );

        alert(response.data.message);
      } catch (error) {
        console.error("Error sending ad request:", error);
        alert("Failed to send ad request.");
      }
    };

    onMounted(() => {
      loadSession();
    });

    return {
      campaigns,
      influencers,
      sponsors,
      searchQuery,
      filteredContent,
      modal,
      role,
      handleFlag,
      showFlagModal,
      flagItem,
      flagItemType,
      flagReason,
      confirmFlag,
      handleRequest,
      usersname,
    };
  },
};
</script>

<style scoped>
.animated-card {
  transition: transform 0.3s, box-shadow 0.3s;
}
.animated-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: bold;
}

.card-body p {
  margin-bottom: 5px;
}

.card-footer .b-button {
  min-width: 80px;
}

.container {
  margin-top: 20px;
}

h4 {
  margin-bottom: 20px;
}
</style>
