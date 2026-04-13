import type { CapturedRequest } from "@/lib/executor/types";

interface NetworkCapture {
  start: () => void;
  stop: () => void;
  waitAndCollect: (ms: number) => Promise<CapturedRequest[]>;
}

function decodeRequestBody(
  requestBody: chrome.webRequest.WebRequestBody | undefined,
): string | undefined {
  if (!requestBody) return undefined;

  if (requestBody.raw && requestBody.raw.length > 0) {
    const parts: string[] = [];
    const decoder = new TextDecoder("utf-8");
    for (const part of requestBody.raw) {
      if (part.bytes) {
        parts.push(decoder.decode(part.bytes));
      }
    }
    if (parts.length > 0) return parts.join("");
  }

  if (requestBody.formData) {
    const entries: string[] = [];
    for (const [key, values] of Object.entries(requestBody.formData)) {
      for (const value of values) {
        entries.push(
          `${encodeURIComponent(key)}=${encodeURIComponent(value)}`,
        );
      }
    }
    if (entries.length > 0) return entries.join("&");
  }

  return undefined;
}

export function createNetworkCapture(tabId: number): NetworkCapture {
  const requests: CapturedRequest[] = [];
  let listener:
    | ((details: chrome.webRequest.WebRequestBodyDetails) => void)
    | null = null;

  const start = () => {
    listener = (details) => {
      const body = decodeRequestBody(details.requestBody);
      requests.push({ url: details.url, ...(body ? { body } : {}) });
    };
    chrome.webRequest.onBeforeRequest.addListener(
      listener,
      { urls: ["<all_urls>"], tabId },
      ["requestBody"],
    );
  };

  const stop = () => {
    if (listener) {
      chrome.webRequest.onBeforeRequest.removeListener(listener);
      listener = null;
    }
  };

  const waitAndCollect = (ms: number): Promise<CapturedRequest[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        stop();
        resolve([...requests]);
      }, ms);
    });
  };

  return { start, stop, waitAndCollect };
}
