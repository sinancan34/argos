interface NetworkCapture {
  start: () => void;
  stop: () => void;
  waitAndCollect: (ms: number) => Promise<string[]>;
}

export function createNetworkCapture(tabId: number): NetworkCapture {
  const requests: string[] = [];
  let listener:
    | ((details: chrome.webRequest.WebRequestBodyDetails) => void)
    | null = null;

  const start = () => {
    listener = (details) => {
      requests.push(details.url);
    };
    chrome.webRequest.onBeforeRequest.addListener(listener, {
      urls: ["<all_urls>"],
      tabId,
    });
  };

  const stop = () => {
    if (listener) {
      chrome.webRequest.onBeforeRequest.removeListener(listener);
      listener = null;
    }
  };

  const waitAndCollect = (ms: number): Promise<string[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        stop();
        resolve([...requests]);
      }, ms);
    });
  };

  return { start, stop, waitAndCollect };
}
