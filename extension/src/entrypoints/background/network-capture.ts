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
        // stream: true carries decoder state across parts. Chrome splits large
        // bodies at arbitrary byte offsets, so a multi-byte character can span
        // two parts — decoding each in isolation would flush it to U+FFFD.
        parts.push(decoder.decode(part.bytes, { stream: true }));
      }
    }
    // Only emit the trailing flush when some part actually carried bytes, so a
    // raw array with no bytes still falls through to the formData branch.
    if (parts.length > 0) return parts.join("") + decoder.decode();
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
      const bodyUnavailable = !body && Boolean(details.requestBody?.error);
      requests.push({
        url: details.url,
        ...(details.method ? { method: details.method } : {}),
        ...(body ? { body } : {}),
        ...(bodyUnavailable ? { bodyUnavailable: true } : {}),
      });
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
