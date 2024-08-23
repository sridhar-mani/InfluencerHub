<template>
  <div class="d-flex p-4">
    <BCard
      v-for="campaign in campaigns"
      :title="campaign.name"
      :key="campaign.id"
      :img-src="base + '/' + campaign.campaign_pic"
      img-alt="Image"
      img-top
      tag="article"
      style="max-width: 15rem; max-height: 28rem"
      class="d-flex flex-column"
    >
      <BCardText
        class="m-0"
        style="height: 30%; font-size: 10px; overflow: hidden"
      >
        {{ campaign.description }}
      </BCardText>

      <BButton
        variant="primary"
        :to="{ name: `OneCampaign`, params: { username: campaign.name } }"
        class="mt-auto m-0 align-self-center"
      >
        Go to Campaign
      </BButton>
    </BCard>

    <BModal
      id="modal-center"
      v-model="modal"
      hide-footer
      centered
      title="Add Campaign"
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
          >Add Campaign</b-button
        >
      </div>
    </BModal>

    <b-button variant="primary" class="fab" @click="openModal"> + </b-button>
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

    const openModal = () => {
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
        console.log("Selected file:", file.name);
        uploadText.value = file.name;
      }
    };
    const { proxy } = getCurrentInstance();

    const submitForm = async () => {
      const formData = new FormData();
      formData.append("name", campaignName.value);
      formData.append("description", campaignDesc.value);
      formData.append("budget", campaignBudget.value);
      formData.append("duration", campaignDuration.value);
      formData.append("niche", campaignNiche.value);
      formData.append("goals", campaignGoals.value);
      formData.append("visibility", campaignVisibility.value);
      if (campaignImg) {
        formData.append("campaign_img", campaignImg.value);
      }

      try {
        const response = await axios.post(
          `http://localhost:5000/add_campaign/${localStorage.getItem(
            "username"
          )}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log("Campaign added successfully", response.data);
        if (response.data.message.toLowerCase().includes("success")) {
          resetForm();
          modal.value = false;
        } else {
          console.log("Campaign not added");
        }
      } catch (error) {
        console.log("Error adding campaign:", error);
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
    };

    onMounted(async () => {
      const role = localStorage.getItem("role");
      if (!role) {
        router.push({ name: "Login" });
      }
      const responce = await axios.get(
        `http://localhost:5000/campaigns/${localStorage.getItem("username")}`
      );
      campaigns.value = responce.data.campaigns;
      console.log(campaigns);
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
