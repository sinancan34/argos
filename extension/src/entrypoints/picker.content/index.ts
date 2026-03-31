import { startPicker } from "@/lib/picker/picker-content-script";

export default defineContentScript({
  matches: ["<all_urls>"],
  registration: "runtime",
  main() {
    startPicker();
  },
});
