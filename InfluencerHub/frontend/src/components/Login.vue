<template>
  <div
    class="d-flex flex-column vh-100 vw-100 justify-content-center align-items-center"
  >
    <div class="w-30">
      <h2 class="d-flex justify-content-center mb-5">Influencer App Login</h2>
      <BForm>
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
        <div class="d-flex w-100 justify-content-evenly mt-3 g-3">
          <BButton type="submit" variant="success" @click="login"
            >Login</BButton
          >
          <BButton type="reset" variant="primary" @click="register"
            >Register</BButton
          >
        </div>
      </BForm>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "Login",
  data() {
    return {
      password: "",
      usernameOrEmail: "",
      loading: false,
    };
  },
  methods: {
    async login() {
      this.loading = true;
      const logindata = this.isEmail(this.usernameOrEmail)
        ? { email: this.usernameOrEmail, password: this.password }
        : { username: this.usernameOrEmail, password: this.password };
      axios
        .post("http://localhost:5000/login", logindata, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then((res) => {
          console.log("login success", res.data);
          localStorage.setItem("username", res.data.user.username);
          localStorage.setItem("role", res.data.user.role);
          this.$router.push({ name: "Home" });
        })
        .catch((err) => {
          console.warn("Wrong Password", err);
        })
        .finally(() => (this.loading = false));
    },
    register() {
      this.$router.push({ name: "Register" });
    },
    isEmail(value) {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailPattern.test(value);
    },
    validateInput() {
      if (this.isEmail(this.usernameOrEmail)) {
        this.email = this.usernameOrEmail;
      } else {
        this.username = this.usernameOrEmail;
      }
    },
  },
};
</script>

<style scoped></style>
