import { defineConfig } from "wxt";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  srcDir: "src",
  modules: ["@wxt-dev/module-react"],
  manifest: {
    name: "Argos GA4 Audit Tool",
    description: "GA4 audit tool for scenario management and testing",
    permissions: ["sidePanel", "activeTab", "tabs", "scripting", "webNavigation"],
    host_permissions: ["<all_urls>"],
    action: {},
  },
  vite: () => ({
    plugins: [tailwindcss()],
  }),
});
