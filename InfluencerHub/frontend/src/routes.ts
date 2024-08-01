import { createRouter, createWebHistory } from "vue-router";
import Login from "./components/Login.vue";
import Home from "./components/Home.vue";
import Register from "./components/Register.vue";
import App from "./App.vue";
import Info from "./components/Info.vue";
import Find from "./components/Find.vue";
import Stats from "./components/Stats.vue";
import Campaign from "./components/Campaign.vue";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/",
    component: App,
    children: [
      {
        path: "",
        name: "Home",
        component: Home,
      },
      {
        path: "info",
        name: "Info",
        component: Info,
      },
      {
        path: "find",
        name: "Find",
        component: Find,
      },
      {
        path: "stats",
        name: "Stats",
        component: Stats,
      },
      {
        path: "campaign",
        name: "Campaign",
        component: Campaign,
      },
    ],
  },

  {
    path: "/register",
    name: "Register",
    component: Register,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
