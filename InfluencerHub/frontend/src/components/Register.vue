<template>
  <div
    class="d-flex flex-column vh-100 vw-100 justify-content-center align-items-center"
  >
    <div class="w-30">
      <h2 class="d-flex justify-content-center mb-5">
        Influencer App Register
      </h2>
      <BForm @submit.prevent="submitForm">
        <BFormFloatingLabel
          :label="role === 'influencer' ? 'Name' : 'Company Name'"
          label-for="floatingName"
          class="my-2"
        >
          <BFormInput
            v-model="name"
            id="floatingName"
            type="text"
            placeholder="Name"
            required
          />
        </BFormFloatingLabel>
        <BFormFloatingLabel
          label="Username"
          label-for="floatingUsername"
          class="my-2"
        >
          <BFormInput
            v-model="username"
            id="floatingUsername"
            type="text"
            placeholder="Username"
            required
          />
        </BFormFloatingLabel>
        <BFormFloatingLabel
          label="Email address"
          label-for="floatingEmail"
          class="my-2"
        >
          <BFormInput
            v-model="email"
            id="floatingEmail"
            type="email"
            placeholder="Email address"
            required
          />
        </BFormFloatingLabel>
        <BFormFloatingLabel
          label="Password"
          label-for="floatingPassword"
          class="my-2"
        >
          <BFormInput
            v-model="password"
            id="floatingPassword"
            type="password"
            autocomplete
            placeholder="Password"
            required
          />
        </BFormFloatingLabel>
        <BFormFloatingLabel
          label="Budget"
          label-for="floatingBudget"
          class="my-2"
          v-if="role === 'sponsor'"
        >
          <BFormInput
            v-model="Budget"
            id="floatingBudget"
            type="number"
            placeholder="Budget"
            required
          />
        </BFormFloatingLabel>

        <BFormFloatingLabel
          :label="role === 'influencer' ? 'Category' : 'Industry'"
          label-for="floatingIndustry"
          class="my-2"
        >
          <BFormInput
            v-model="industry"
            id="floatingIndustry"
            type="text"
            :placeholder="role === 'influencer' ? 'Category' : 'Industry'"
            required
          />
        </BFormFloatingLabel>
        <BFormSelect
          v-model="role"
          :options="exFieldNamesOptions"
          class="mb-2"
          value-field="name"
          text-field="item"
          required
        />
        <BFormGroup
          label-for="tags-component-select"
          v-if="role === 'influencer'"
        >
          <BFormSelect
            id="tags-component-select"
            v-model="selectedTag"
            :options="availableOptions"
            class="mb-2"
            @click="addTag"
          >
          </BFormSelect>
          <ul v-if="niche.length > 0" class="list-inline d-inline-block mb-2">
            <li v-for="tag in niche" :key="tag" class="list-inline-item">
              <BFormTag @remove="removeTag(tag)" :title="tag" variant="info">
                {{ tag }}
              </BFormTag>
            </li>
          </ul>
        </BFormGroup>
        <BFormGroup label-for="influencer-img">
          <div class="image-uploader">
            <input
              type="file"
              id="influencer-img"
              accept="image/*"
              class="file-input"
              @change="handleFileChange"
            />
            <label for="influencer-img" class="upload-label">
              <span class="upload-text">Choose an image...</span>
            </label>
          </div>
        </BFormGroup>

        <div class="mt-3 text-center">
          You are a <strong>{{ role }}</strong>
        </div>
        <div class="d-flex w-100 justify-content-evenly mt-3 g-3">
          <BButton type="submit" variant="success">Register</BButton>
          <BButton type="button" variant="primary" @click="login"
            >Login</BButton
          >
        </div>
      </BForm>
    </div>
  </div>
</template>
<script>
import { ref, computed } from "vue";
import axios from "axios";
import router from "../routes";

export default {
  name: "Register",
  setup() {
    const name = ref("");
    const username = ref("");
    const email = ref("");
    const password = ref("");
    const role = ref("influencer");
    const industry = ref("");
    const niche = ref([]);
    const Budget = ref(0);
    const selectedTag = ref("Select your niche");
    const options = ref([
      "Youtube",
      "Instagram",
      "Facebook",
      "Tiktok",
      "Select your niche",
    ]);
    const profilepic = ref(null);

    const handleFileChange = () => {
      const file = document.getElementById("influencer-img").files[0];
      profilepic.value = file;
      console.log(profilepic.value);
      if (file && file.type.startsWith("image/")) {
        profilepic.value = file;
        document.querySelector(".upload-text").textContent = file.name;
        console.log("File uploaded:", profilepic.value.name);
      } else {
        console.log("Invalid file type. Please upload an image.");
      }
    };

    const exFieldNamesOptions = [
      { item: "Influencer", name: "influencer" },
      { item: "Sponsor", name: "sponsor" },
    ];

    const availableOptions = computed(() => {
      return options.value.filter((opt) => !niche.value.includes(opt));
    });

    const addTag = () => {
      if (
        selectedTag.value &&
        !niche.value.includes(selectedTag.value) &&
        selectedTag.value !== "Select your niche"
      ) {
        niche.value.push(selectedTag.value);
        selectedTag.value = "";
      }
    };
    const removeTag = (tag) => {
      niche.value = niche.value.filter((t) => t !== tag);
    };

    const submitForm = async () => {
      try {
        const formData = new FormData();
        formData.append("username", username.value);
        formData.append("email", email.value);
        formData.append("password", password.value);
        formData.append("role", role.value.toLowerCase());

        if (role.value.toLowerCase() === "influencer") {
          formData.append("name", name.value);
          formData.append("profile_name", name.value);
          formData.append("category", industry.value);
          formData.append("niche", JSON.stringify(niche.value));
          if (profilepic.value) {
            formData.append("profile_pic", profilepic.value);
          } else {
            console.log("No profile picture selected");
          }
        } else if (role.value.toLowerCase() === "sponsor") {
          formData.append("companyname", name.value);
          formData.append("industry", industry.value);
          formData.append("budget", Budget.value);
          formData.append("profile_pic", profilepic.value);
        }
        const response = await axios.post(
          "http://localhost:5000/register",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        if (response.data.message.toLowerCase().includes("success")) {
          router.push({ name: "Login" });
        } else {
          console.log("User not created");
        }
      } catch (error) {
        console.error("Error registering user:", error);
      }
    };

    const login = () => {
      router.push({ name: "Login" });
    };

    return {
      name,
      username,
      email,
      password,
      role,
      industry,
      niche,
      selectedTag,
      options,
      availableOptions,
      exFieldNamesOptions,
      addTag,
      submitForm,
      login,
      removeTag,
      Budget,
      handleFileChange,
    };
  },
};
</script>

<style scoped>
.w-30 {
  width: 30%;
}

@media (max-width: 768px) {
  .w-30 {
    width: 90%;
  }
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
