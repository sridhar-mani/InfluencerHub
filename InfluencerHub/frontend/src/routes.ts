// router.js
import { createRouter, createWebHistory } from "vue-router";
import Home from "./components/Home.vue";
import Info from "./components/Info.vue";
import Find from "./components/Find.vue";
import Stats from "./components/Stats.vue";
import Campaign from "./components/Campaign.vue";
import Profile from "./components/Profile.vue";
import OneCampaign from "./components/OneCampaign.vue";

const routes = [
  {
    path: "/register",
    name: "Register",
    component: () => import("./components/Register.vue"),
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("./components/Login.vue"),
  },

  {
    path: "/",
    name: "Home",
    component: Home,
    children: [
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
      {
        path: "campaigns/:username?",
        name: "OneCampaign",
        component: OneCampaign,
        props: true,
      },
      {
        path: "profile",
        name: "Profile",
        component: Profile,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
