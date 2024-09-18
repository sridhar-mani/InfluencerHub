<template>
  <div
    class="d-flex flex-column vh-100 vw-100 justify-content-center align-items-center"
  >
    <Teleport to="body">
      <div :class="'top-0 end-0'" class="toast-container position-fixed p-3">
        <BToast v-model="showToast" class="specialPop">
          <template #title>{{ message }}</template>
          {{ message }}
        </BToast>
      </div>
    </Teleport>
    <div class="w-30">
      <h2 class="d-flex justify-content-center mb-5">Influencer App Login</h2>

      <BForm @submit.prevent="login">
        <BFormFloatingLabel
          label="Username or Email Address"
          label-for="floatingInput"
          class="my-2"
        >
          <BFormInput
            id="floatingInput"
            type="text"
            placeholder="Username or Email Address"
            v-model="usernameOrEmail"
            @input="validateInput"
          />
        </BFormFloatingLabel>
        <BFormFloatingLabel
          label="Password"
          label-for="floatingPassword"
          class="my-2"
        >
          <BFormInput
            id="floatingPassword"
            type="password"
            autocomplete
            v-model="password"
            placeholder="Password"
          />
        </BFormFloatingLabel>
        <template> </template>
        <div class="d-flex w-100 justify-content-evenly mt-3 g-3">
          <BButton type="submit" variant="success" @click.prevent="login"
            >Login</BButton
          >
          <BButton type="button" variant="primary" @click="register"
            >Register</BButton
          >
        </div>
      </BForm>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref } from "vue";
import router from "../routes";
import { useToast } from "bootstrap-vue-next";

export default {
  name: "Login",
  setup() {
    const usernameOrEmail = ref("");
    const password = ref("");
    const showToast = ref(false);
    const show = ref(false);
    const message = ref("");

    const login = async () => {
      try {
        const loginData = {
          username: usernameOrEmail.value,
          password: password.value,
        };
        if (
          loginData.username === "" ||
          loginData.password === "" ||
          loginData.username === null ||
          loginData.password === null
        ) {
          message.value = "Please fill in all fields";
          showToast.value = true;
          return;
        }
        const response = await axios.post(
          "http://localhost:5000/login",
          loginData,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        console.log("login success", response.data);
        if (response.data) {
          localStorage.setItem("username", response.data.user.username);
          localStorage.setItem("role", response.data.user.role);
          localStorage.setItem("token", response.data.token);
          router.push({ name: "Find" });
        }
      } catch (err) {
        const toastComp = document.getElementsByClassName("specialPop")[0];
        if (err.response) {
          toastComp.style.backgroundColor = "red";
        }
        if (err.response?.status === 401) {
          message.value = "Invalid username or password";
          showToast.value = true;
        }
        if (err.response?.status === 500) {
          message.value = "Server error";
          showToast.value = true;
        }
        if (err.response?.status === 404) {
          message.value = "User not found";
          showToast.value = true;
        }
      }
    };

    const register = () => {
      router.push({ name: "Register" });
    };

    const isEmail = (value) => {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailPattern.test(value);
    };

    const validateInput = () => {
      if (isEmail(usernameOrEmail.value)) {
        // do something with email
      } else {
        // do something with username
      }
    };

    return {
      usernameOrEmail,
      password,
      showToast,
      login,
      register,
      validateInput,
      show,
      message,
    };
  },
};
</script>

<style scoped></style>
