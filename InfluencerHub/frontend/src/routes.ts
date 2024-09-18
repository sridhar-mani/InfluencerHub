// router.js
import { createRouter, createWebHistory } from "vue-router";
import Home from "./components/Home.vue";
import Info from "./components/Info.vue";
import Find from "./components/Find.vue";
import Stats from "./components/Stats.vue";
import Campaign from "./components/Campaign.vue";
import Profile from "./components/Profile.vue";
import OneCampaign from "./components/OneCampaign.vue";
import OneProfile from "./components/OneProfile.vue";

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
    redirect: () => {
      const role = localStorage.getItem("role");
      if (role === "admin" || role === "influencer" || role === "sponsor") {
        return "/home/find";
      } else {
        return "/login";
      }
    },
  },
  {
    path: "/",
    name: "Home",
    component: Home,
    meta: { requiresAuth: true },
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
        path: "profile/:username?",
        name: "OneProfile",
        component: OneProfile,
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

router.beforeEach((to, from, next) => {
  const role = localStorage.getItem("role");
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (role === "admin" || role === "influencer" || role === "sponsor") {
      next();
    } else {
      next({ name: "Login" });
    }
  } else {
    next();
  }
});

export default router;
