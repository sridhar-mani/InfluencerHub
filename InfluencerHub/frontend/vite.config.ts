import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import envCompatible from "vite-plugin-env-compatible";

export default defineConfig({
  plugins: [vue(), envCompatible({ prefix: "VITE_APP_", path: "../.env" })],
  server: {
    proxy: {
      "/api": "http://localhost:5000",
    },
  },
});
