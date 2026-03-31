import type { ContentResponse } from "@/lib/messaging/types";
import { waitForActionable } from "@/lib/executor/actionability";
import type { SelectorEntry } from "@/lib/commands";

async function handleClick(
  selectors: SelectorEntry[],
  timeout: number,
): Promise<ContentResponse> {
  try {
    const element = await waitForActionable(selectors, timeout);
    element.click();
    return { success: true };
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: message };
  }
}

export default defineContentScript({
  matches: ["<all_urls>"],
  registration: "runtime",
  main() {
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      if (message.type === "EXEC_CLICK") {
        handleClick(message.selectors, message.timeout).then(sendResponse);
        return true;
      }
    });

    chrome.runtime.sendMessage({ type: "CONTENT_READY" });
  },
});
