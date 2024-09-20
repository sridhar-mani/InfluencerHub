<template>
  <div class="d-flex p-4 campaign-cards">
    <BCard
      v-for="campaign in campaigns"
      :key="campaign.id"
      class="custom-card p-0"
    >
      <div class="card-image-wrapper">
        <img
          :src="
            campaign.campaign_pic
              ? base + '/' + campaign.campaign_pic
              : base + '/static/call-out-2702440_640.png'
          "
          alt="Image"
          class="card-image"
        />
      </div>
      <div class="card-details-overlay">
        <div class="details-content">
          <h4 class="card-title">{{ campaign.name }}</h4>
          <p class="card-description">{{ campaign.description }}</p>
          <p class="card-budget">Budget: {{ campaign.budget }}</p>
          <div class="card-buttons">
            <BButton
              variant="danger"
              class="btn-delete"
              @click="() => deleteCampaign(campaign.id)"
            >
              Delete
            </BButton>
            <BButton
              variant="warning"
              @click="openModal(campaign)"
              class="btn-edit"
            >
              Edit
            </BButton>
          </div>
          <div class="card-footer">
            <BButton
              variant="primary"
              :to="{
                name: `OneCampaign`,
                params: { username: campaign.name, name: username },
              }"
              class="btn-view"
            >
              Go to Campaign
            </BButton>
          </div>
        </div>
      </div>
    </BCard>
    <BModal
      id="campaign-modal"
      v-model="modal"
      hide-footer
      centered
      title="Edit Campaign"
    >
      <BContainer fluid>
        <BRow>
          <BCol cols="12" md="6">
            <b-form-group label="Campaign Title:" label-for="campaign-name">
              <b-form-input
                id="campaign-name"
                v-model="campaignName"
                required
              ></b-form-input>
            </b-form-group>
          </BCol>
          <BCol cols="12" md="6">
            <b-form-group
              label="Campaign Visibility:"
              label-for="campaign-visibility"
            >
              <div class="d-flex gap-3">
                <BFormRadio
                  v-model="campaignVisibility"
                  name="some-radios"
                  value="public"
                  >Public
                </BFormRadio>
                <BFormRadio
                  v-model="campaignVisibility"
                  name="some-radios"
                  value="private"
                  >Private
                </BFormRadio>
              </div>
            </b-form-group>
          </BCol>
        </BRow>

        <BRow>
          <BCol cols="12" md="6">
            <b-form-group
              label="Campaign Description:"
              label-for="campaign-desc"
            >
              <b-form-textarea
                id="campaign-desc"
                v-model="campaignDesc"
                required
              ></b-form-textarea>
            </b-form-group>
          </BCol>

          <BCol cols="12" md="6">
            <b-form-group label="Campaign Image:" label-for="campaign-img">
              <div class="image-uploader">
                <input
                  type="file"
                  id="campaign-img"
                  class="file-input"
                  @change="handleFileChange"
                />
                <label for="campaign-img" class="upload-label">
                  <span class="upload-text">{{ uploadText }}</span>
                </label>
              </div>
            </b-form-group>
          </BCol>
        </BRow>

        <BRow>
          <BCol cols="12" md="6">
            <b-form-group
              label="Campaign Duration:"
              label-for="campaign-duration"
            >
              <b-form-input
                id="campaign-duration"
                v-model="campaignDuration"
                type="number"
                min="7"
                required
              ></b-form-input>
            </b-form-group>
          </BCol>
          <BCol cols="12" md="6">
            <b-form-group label="Campaign Budget:" label-for="campaign-budget">
              <b-form-input
                type="number"
                min="0"
                id="campaign-budget"
                v-model="campaignBudget"
                required
              ></b-form-input>
            </b-form-group>
          </BCol>
        </BRow>

        <BRow>
          <BCol cols="12" md="6">
            <BFormGroup
              label="Campaign Niche"
              label-for="tags-component-select"
            >
              <BFormSelect
                id="tags-component-select"
                v-model="selectedTag"
                :options="availableOptions"
                class="mb-2"
                @click="addTag"
              >
              </BFormSelect>
              <ul
                v-if="campaignNiche.length > 0"
                class="list-inline d-inline-block mb-2"
              >
                <li
                  v-for="tag in campaignNiche"
                  :key="tag"
                  class="list-inline-item"
                >
                  <BFormTag
                    @remove="removeTag(tag)"
                    :title="tag"
                    variant="info"
                  >
                    {{ tag }}
                  </BFormTag>
                </li>
              </ul>
            </BFormGroup>
          </BCol>
          <BCol cols="12" md="6">
            <b-form-group label="Campaign Goals:" label-for="campaign-goals">
              <b-form-input
                id="campaign-goals"
                v-model="campaignGoals"
                required
              ></b-form-input>
            </b-form-group>
          </BCol>
        </BRow>
      </BContainer>
      <div class="w-100 d-flex justify-content-center">
        <b-button type="submit" @click="submitForm" variant="success"
          >Save Changes</b-button
        >
      </div>
    </BModal>

    <!-- Floating Button for Adding a New Campaign -->
    <BButton variant="primary" class="fab" @click="openModal()"> + </BButton>
  </div>
</template>

<script>
import { ref, computed, getCurrentInstance, onMounted } from "vue";
import { BContainer, BRow, BToast } from "bootstrap-vue-next";
import axios from "axios";
import Toast from "./Toast.vue";

export default {
  name: "Campaign",
  setup() {
    const campaignImg = ref(null);
    const campaignName = ref("");
    const campaignDesc = ref("");
    const campaignBudget = ref(0);
    const campaignDuration = ref(0);
    const campaignNiche = ref([]);
    const campaignGoals = ref("");
    const uploadText = ref("Choose an image...");
    const campaignVisibility = ref("public");
    const selectedTag = ref("Select your niche");
    const modal = ref(false);
    const base = import.meta.env.VITE_APP_API_BASE_URL;
    const options = ref([
      "Youtube",
      "Instagram",
      "Facebook",
      "Tiktok",
      "Select your niche",
    ]);
    const campaigns = ref([]);
    const editingCampaignId = ref(null);
    const username = ref("");
    const openModal = (campaign = null) => {
      if (campaign) {
        const start =
          campaign.start_date &&
          campaign.start_date.split(", ")[1].split(" ")[0];
        const end =
          campaign.end_date && campaign.end_date.split(", ")[1].split(" ")[0];
        editingCampaignId.value = campaign.id;
        campaignName.value = campaign.name;
        campaignDesc.value = campaign.description;
        campaignBudget.value = campaign.budget;
        campaignDuration.value = end - start;
        campaignNiche.value = campaign.niche.split(",");
        campaignGoals.value = campaign.goals;
        campaignVisibility.value = campaign.visibility;
        uploadText.value = campaign.campaign_pic
          ? "Change Image"
          : "Choose an image...";
      } else {
        // Add mode - reset the form
        resetForm();
      }
      modal.value = true;
    };

    const availableOptions = computed(() => {
      return options.value.filter((opt) => !campaignNiche.value.includes(opt));
    });

    const addTag = () => {
      if (
        selectedTag.value &&
        !campaignNiche.value.includes(selectedTag.value) &&
        selectedTag.value !== "Select your niche"
      ) {
        campaignNiche.value.push(selectedTag.value);
        selectedTag.value = "";
      }
    };

    const removeTag = (tag) => {
      campaignNiche.value = campaignNiche.value.filter((t) => t !== tag);
    };

    const handleFileChange = (event) => {
      const file = event.target.files[0];
      campaignImg.value = file;
      if (file) {
        uploadText.value = file.name;
      }
    };

    // Submit form data for adding or editing a campaign
    const submitForm = async () => {
      const formData = new FormData();
      formData.append("name", campaignName.value);
      formData.append("description", campaignDesc.value);
      formData.append("budget", campaignBudget.value);
      formData.append("duration", campaignDuration.value);
      formData.append("niche", campaignNiche.value);
      formData.append("goals", campaignGoals.value);
      formData.append("visibility", campaignVisibility.value);
      if (campaignImg.value) {
        formData.append("campaign_img", campaignImg.value);
      }

      try {
        // Determine whether to edit or create
        let apiUrl = `http://localhost:5000/add_campaign/${localStorage.getItem(
          "username"
        )}`;
        let method = "post"; // POST for both add and edit in this implementation

        const response = await axios({
          method: method,
          url: apiUrl,
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        console.log(response.data.message);
        if (response.status === 200 || response.status === 201) {
          resetForm();
          modal.value = false;
          // Update campaigns list after adding or editing
          await loadCampaigns();
        } else {
          console.log("Campaign not added/updated");
        }
      } catch (error) {
        console.log("Error adding/updating campaign:", error);
      }
    };

    const resetForm = () => {
      campaignName.value = "";
      campaignDesc.value = "";
      campaignBudget.value = 0;
      campaignDuration.value = 0;
      campaignNiche.value = [];
      campaignGoals.value = "";
      campaignVisibility.value = "public";
      campaignImg.value = null;
      editingCampaignId.value = null; // Reset the editing ID
      uploadText.value = "Choose an image...";
    };
    const deleteCampaign = async (id) => {
      try {
        console.log(id);
        const token = localStorage.getItem("token"); // Ensure the token is
        const res = await axios.post(
          "http://localhost:5000/delete_campaign",
          { campaign_id: id },
          {
            headers: {
              Authorization: `Bearer ${token}`, // Add the Authorization header
            },
          }
        );

        if (res.status === 200) {
          await loadCampaigns(); // Reload campaigns if deletion is successful
        } else {
          console.error("Error deleting campaign:", res.data.message);
        }
      } catch (error) {
        console.error("Error deleting campaign:", error);
      }
    };

    const loadCampaigns = async () => {
      const response = await axios.get(
        `http://localhost:5000/campaigns/${localStorage.getItem("username")}`
      );
      campaigns.value = response.data.campaigns;
      username.value = localStorage.getItem("username");
    };

    onMounted(async () => {
      await loadCampaigns();
    });

    return {
      campaignImg,
      campaignName,
      campaignDesc,
      campaignBudget,
      campaignDuration,
      campaignNiche,
      uploadText,
      campaignGoals,
      openModal,
      campaignVisibility,
      selectedTag,
      modal,
      options,
      availableOptions,
      addTag,
      removeTag,
      handleFileChange,
      resetForm,
      submitForm,
      campaigns,
      base,
      deleteCampaign,
      username,
    };
  },
};
</script>

<style scoped>
.fab {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease;
}

.fab:hover {
  background-color: #0056b3;
}

.custom-card {
  max-width: 20rem; /* Increase width */
  max-height: 35rem; /* Increase height */
  display: flex;
  flex-direction: column;
  margin: 1rem;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.custom-card:hover {
  transform: scale(1.05);
}

.card-image-wrapper {
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 250px; /* Adjusted height for larger image */
  object-fit: cover;
}

.card-details-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 1rem;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.custom-card:hover .card-details-overlay {
  opacity: 1;
  visibility: visible;
}

.details-content {
  text-align: center;
}

.card-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.card-description {
  margin: 1rem 0;
  font-size: 1rem;
}

.card-budget {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.card-buttons,
.card-footer {
  display: flex;
  justify-content: space-around;
  padding: 0.5rem;
}

.btn-delete,
.btn-edit,
.btn-view {
  flex: 1;
  margin: 0.2rem;
}
.image-uploader {
  position: relative;
  overflow: hidden;
  display: inline-block;
  width: 100%;
  height: 50px;
  border: 2px dashed #007bff;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  text-align: center;
  background-color: #f9f9f9;
  color: #007bff;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-label {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  color: #007bff;
}

.upload-text {
  pointer-events: none;
}

.image-uploader:hover {
  background-color: #f0f8ff;
}
</style>
