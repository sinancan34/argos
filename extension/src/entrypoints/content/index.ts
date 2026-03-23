import type { SelectorEntry } from "@/lib/commands";
import type { ContentResponse } from "@/lib/messaging/types";

function findElement(selectors: SelectorEntry[]): HTMLElement | null {
  for (const { strategy, value } of selectors) {
    let element: Element | null = null;

    switch (strategy) {
      case "css":
        element = document.querySelector(value);
        break;

      case "xpath":
        element = document.evaluate(
          value,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null,
        ).singleNodeValue as Element | null;
        break;

      case "linkText":
        element =
          Array.from(document.querySelectorAll("a")).find(
            (a) => a.textContent?.trim() === value,
          ) ?? null;
        break;
    }

    if (element instanceof HTMLElement) {
      return element;
    }
  }

  return null;
}

function handleClick(selectors: SelectorEntry[]): ContentResponse {
  const element = findElement(selectors);

  if (element) {
    element.click();
    return { success: true };
  }

  return { success: false, error: "No element found for any selector" };
}

export default defineContentScript({
  matches: ["<all_urls>"],
  registration: "runtime",
  main() {
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      if (message.type === "EXEC_CLICK") {
        const result = handleClick(message.selectors);
        sendResponse(result);
        return true;
      }
    });

    chrome.runtime.sendMessage({ type: "CONTENT_READY" });
  },
});
