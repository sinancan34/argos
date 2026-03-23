import { defineConfig } from "wxt";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  srcDir: "src",
  modules: ["@wxt-dev/module-react"],
  manifest: {
    name: "Argos Pixel Code Audit Tool",
    description: "Pixel code audit tool for scenario management and testing",
    permissions: ["sidePanel", "activeTab", "tabs", "scripting", "webNavigation", "webRequest"],
    host_permissions: ["<all_urls>"],
    action: {},
  },
  vite: () => ({
    plugins: [tailwindcss()],
  }),
});
