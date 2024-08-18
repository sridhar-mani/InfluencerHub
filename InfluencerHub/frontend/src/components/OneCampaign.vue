  <template>
    <div class="container mt-0">
      <b-card class="mb-1">
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
          style="height: 300px; width: 300px; maxWidth: 100%;"
        ></b-card-img>

        <b-card-text class="mb-0">
          <b-row>
            <b-col>
              <p class="mb-2"><strong>Description:</strong> {{ campaign.description }}</p>
              <p class="mb-2"><strong>Budget:</strong> ${{ campaign.budget }}</p>
              <p class="mb-2"><strong>Visibility:</strong> {{ campaign.visibility }}</p>
              <p class="mb-2"><strong>Goals:</strong> {{ campaign.goals }}</p>
              <p class="mb-0"><strong>Niche:</strong> {{ campaign.niche }}</p>
            </b-col>

            <b-col class="d-flex justify-content-end align-items-end">
              <b-button @click="openModal" variant="success" style="font-size: 30px; width: 70px; height: 70px; display:flex; justify-content: center; align-items: center; border-radius: 50%;">+</b-button>
            </b-col>
          </b-row>
        </b-card-text>
        
        <b-modal
          id="modal-center"
          v-model="modal"
          hide-footer
          centered
          title="Add Ad Request"
        >
          <b-container fluid>
            <b-row>
              <b-form @submit.prevent="submitAdRequest" v-if="userRole === 'sponsor'">
                <b-form-group label="Name:" label-for="name">
                  <b-form-input
                    id="name"
                    v-model="adRequest.name"
                    required
                  ></b-form-input>
                </b-form-group>
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
                <b-form-group label="Proposed Payment Amount:" label-for="payment-amount">
                  <b-form-input
                    id="payment-amount"
                    v-model.number="adRequest.payment_amount"
                    type="number"
                    required
                  ></b-form-input>
                </b-form-group>
                <b-form-group label="Influencers:" label-for="influencers">
                  <b-input-group>
                    <b-form-input
                      id="influencers"
                      v-model="influencerQuery"
                      @input="fetchSuggestions"
                
                      @focus="fetchSuggestions"
                      autocomplete="off"
                    ></b-form-input>

                    <b-input-group-append>
                      <b-button @click="fetchSuggestions" variant="primary">Find</b-button>
                    </b-input-group-append>
                  </b-input-group>
                </b-form-group>

                <div v-if="showSuggestions" class="mt-2">
                  <div v-for="s in suggestions" :key="s">
                    <label>
                      <input 
                        type="checkbox" 
                        :value="s"
                        :on-change="handleCheckboxChange"
                        v-model="selectedSuggestion" 
                      />
                      {{ s }}
                    </label>
                  </div>
                </div>
                
                
                
                <div class="w-100 d-flex justify-content-center">
                  <b-button type="submit" variant="success">Submit Ad Request</b-button>
                </div>
              </b-form>
            </b-row>
          </b-container>
        </b-modal>
      </b-card>
      <b-button variant="primary" :to="{name:'Campaign'}">Back to Campaign List</b-button>
    </div>
  </template>

  <script>
  import { ref, onMounted } from "vue";
  import axios from "axios";
  import { useRoute } from "vue-router";
  import { BContainer, BRow, BToast } from "bootstrap-vue-next";

  export default {
    name: "OneCampaign",
    components: { BContainer, BRow, BToast },
    setup() {
      const route = useRoute();
      const campaignimg = ref("");
      const campaign = ref({});
      const modal = ref(false);
      const selectedSuggestion = ref([]); // Should be an empty array
      const selectedInfluencers = ref([]);
      const userRole = ref(localStorage.getItem("role") || "");
      const adRequest = ref({
        name: "",
        message: "",
        requirements: "",
        payment_amount: 0,
        influencers: []
      });
      const influencerQuery = ref("");
      const suggestions = ref([]);
      const showSuggestions = ref(false);

      const openModal = () => {
        modal.value = !modal.value;
      };

      const handleCheckboxChange = (event) => {
      const value = event.target.value;
      const checked = event.target.checked;
      if (checked) {
        if (!selectedSuggestion.value.includes(value)) {
          selectedSuggestion.value.push(value);
        }
      } else {
        selectedSuggestion.value = selectedSuggestion.value.filter(s => s !== value);
      }
    };

      const loadCampaign = async () => {
        try {
          const name = localStorage.getItem("username");
          const response = await axios.get(
            `http://localhost:5000/campaign/${localStorage.getItem('username')}/${route.params.username}`
          );
          campaign.value = response.data[0];
          console.log(campaign);
          campaignimg.value = `${import.meta.env.VITE_APP_API_BASE_URL}/${campaign.value.campaign_pic}`;
        } catch (error) {
          console.error("Error loading campaign:", error);
        }
      };

      const submitAdRequest = async () => {
    try {
      adRequest.value.influencers = selectedSuggestion.value; 
      const response = await axios.post(
        `http://localhost:5000/add_adrequest/${localStorage.getItem("username")}/${campaign.value.id}`,
        adRequest.value
      );
      console.log(response);
      adRequest.value = {
        name: "",
        message: "",
        requirements: "",
        payment_amount: 0,
        influencers: []
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
    if (query.length > 1) {
      try {
        const response = await axios.get(`http://localhost:5000/users/get_influencers`, {
          params: { query }
        });
        console.log('API response:', response.data);
        suggestions.value = response.data;
        console.log('Suggestions:', suggestions.value,showSuggestions.value); 
        showSuggestions.value = true;
        console.log(selectedSuggestion.value);
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
        fetchSuggestions,
      
      };
    }
  };
  </script>

  <style scoped>
  </style>
