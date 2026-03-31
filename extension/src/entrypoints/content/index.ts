import type { ContentResponse } from "@/lib/messaging/types";
import { waitForActionable } from "@/lib/executor/actionability";

async function handleClick(
  selector: string,
  timeout: number,
): Promise<ContentResponse> {
  try {
    const element = await waitForActionable(selector, timeout);
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
        handleClick(message.selector, message.timeout).then(sendResponse);
        return true;
      }
    });

    chrome.runtime.sendMessage({ type: "CONTENT_READY" });
  },
});
