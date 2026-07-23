import { defineConfig } from "wxt";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  srcDir: "src",
  outDir: "output",
  modules: ["@wxt-dev/module-react"],
  manifest: {
    name: "Argos Pixel Code Audit Tool",
    description: "Pixel code audit tool for scenario management and testing",
    permissions: [
      "activeTab",
      "tabs",
      "scripting",
      "webNavigation",
      "webRequest",
      // Device emulation attaches chrome.debugger to the execution tab and drives
      // the CDP Emulation domain (viewport/DPR/mobile/touch/UA) — the same protocol
      // DevTools' Device Toolbar uses. Attached only for the duration of a run.
      "debugger",
    ],
    host_permissions: ["<all_urls>"],
  },
  vite: () => ({
    plugins: [tailwindcss()],
  }),
});
