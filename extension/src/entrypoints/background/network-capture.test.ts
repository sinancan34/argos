import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  installChromeMock,
  uninstallChromeMock,
  toRawBytes,
  type ChromeMock,
  type WebRequestFilter,
} from "@/test/chrome-mock";
import { createNetworkCapture } from "./network-capture";

const TAB_ID = 42;
const WAIT_MS = 5000;
const COLLECT_URL = "https://analytics.example.com/g/collect?v=2&tid=G-ABC123";

let chromeMock: ChromeMock;

/** The filter object passed to onBeforeRequest.addListener. */
function registeredFilter(): WebRequestFilter {
  const call = chromeMock.webRequest.onBeforeRequest.addListener.mock.calls[0];
  if (!call) throw new Error("addListener was not called");
  return call[1] as WebRequestFilter;
}

function registeredExtraInfoSpec(): string[] {
  const call = chromeMock.webRequest.onBeforeRequest.addListener.mock.calls[0];
  if (!call) throw new Error("addListener was not called");
  return call[2] as string[];
}

describe("createNetworkCapture — listener registration", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.restoreAllMocks();
  });

  it("registers no listener until start is called", () => {
    // Arrange
    createNetworkCapture(TAB_ID);

    // Act
    const callCount =
      chromeMock.webRequest.onBeforeRequest.addListener.mock.calls.length;

    // Assert
    expect(callCount).toBe(0);
  });

  it("registers a listener on start", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);

    // Act
    capture.start();

    // Assert
    expect(chromeMock.webRequest.onBeforeRequest.addListener).toHaveBeenCalledTimes(
      1,
    );
  });

  it("scopes the filter to the execution tab", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);

    // Act
    capture.start();

    // Assert
    expect(registeredFilter().tabId).toBe(TAB_ID);
  });

  it("listens across all urls", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);

    // Act
    capture.start();

    // Assert
    expect(registeredFilter().urls).toEqual(["<all_urls>"]);
  });

  it("requests the requestBody extra info so payloads are visible", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);

    // Act
    capture.start();

    // Assert
    expect(registeredExtraInfoSpec()).toEqual(["requestBody"]);
  });

  it("removes the listener on stop", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();

    // Act
    capture.stop();

    // Assert
    expect(chromeMock.webRequest.onBeforeRequest.listenerCount).toBe(0);
  });

  it("removes the same listener instance it registered", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    const registered =
      chromeMock.webRequest.onBeforeRequest.addListener.mock.calls[0][0];

    // Act
    capture.stop();

    // Assert
    expect(
      chromeMock.webRequest.onBeforeRequest.removeListener,
    ).toHaveBeenCalledWith(registered);
  });

  it("ignores a stop before start", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);

    // Act
    capture.stop();

    // Assert
    expect(
      chromeMock.webRequest.onBeforeRequest.removeListener,
    ).not.toHaveBeenCalled();
  });

  it("ignores a repeated stop", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    capture.stop();

    // Act
    capture.stop();

    // Assert
    expect(
      chromeMock.webRequest.onBeforeRequest.removeListener,
    ).toHaveBeenCalledTimes(1);
  });

  it("registers a fresh listener when restarted", () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    capture.stop();

    // Act
    capture.start();

    // Assert
    expect(chromeMock.webRequest.onBeforeRequest.listenerCount).toBe(1);
  });

  it("keeps two captures independent", () => {
    // Arrange
    const first = createNetworkCapture(TAB_ID);
    const second = createNetworkCapture(TAB_ID + 1);
    first.start();
    second.start();

    // Act
    first.stop();

    // Assert
    expect(chromeMock.webRequest.onBeforeRequest.listenerCount).toBe(1);
  });
});

describe("createNetworkCapture — request collection", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    vi.useFakeTimers();
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  /** Starts a capture, emits the given requests, and resolves the collected list. */
  async function captureAll(
    details: Array<Parameters<typeof chromeMock.webRequest.onBeforeRequest.emit>[0]>,
  ) {
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    for (const detail of details) {
      chromeMock.webRequest.onBeforeRequest.emit(detail);
    }
    const collected = capture.waitAndCollect(WAIT_MS);
    await vi.advanceTimersByTimeAsync(WAIT_MS);
    return collected;
  }

  it("collects the url of a captured request", async () => {
    // Arrange & Act
    const requests = await captureAll([{ url: COLLECT_URL }]);

    // Assert
    expect(requests[0].url).toBe(COLLECT_URL);
  });

  it("collects nothing when no request fired", async () => {
    // Arrange & Act
    const requests = await captureAll([]);

    // Assert
    expect(requests).toEqual([]);
  });

  it("omits the body key when the request has no body", async () => {
    // Arrange & Act
    const requests = await captureAll([{ url: COLLECT_URL }]);

    // Assert
    expect(requests[0]).not.toHaveProperty("body");
  });

  it("records the request method", async () => {
    // Arrange & Act
    const requests = await captureAll([{ url: COLLECT_URL, method: "POST" }]);

    // Assert
    expect(requests[0].method).toBe("POST");
  });

  it("omits the method key when Chrome reports none", async () => {
    // Arrange & Act
    const requests = await captureAll([{ url: COLLECT_URL }]);

    // Assert
    expect(requests[0]).not.toHaveProperty("method");
  });

  it("flags a body Chrome could not expose", async () => {
    // Arrange & Act — Chrome sets requestBody.error when the bytes are unavailable
    const requests = await captureAll([
      { url: COLLECT_URL, method: "POST", requestBody: { error: "blocked" } },
    ]);

    // Assert
    expect(requests[0].bodyUnavailable).toBe(true);
  });

  it("omits the unavailable flag when the body decoded fine", async () => {
    // Arrange & Act
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        method: "POST",
        requestBody: { raw: [{ bytes: toRawBytes("en=page_view") }] },
      },
    ]);

    // Assert
    expect(requests[0]).not.toHaveProperty("bodyUnavailable");
  });

  it("collects requests in the order they fired", async () => {
    // Arrange & Act
    const requests = await captureAll([
      { url: "https://a.example.com/1" },
      { url: "https://b.example.com/2" },
    ]);

    // Assert
    expect(requests.map((r) => r.url)).toEqual([
      "https://a.example.com/1",
      "https://b.example.com/2",
    ]);
  });

  it("keeps duplicate urls as separate entries", async () => {
    // Arrange & Act
    const requests = await captureAll([
      { url: COLLECT_URL },
      { url: COLLECT_URL },
    ]);

    // Assert
    expect(requests).toHaveLength(2);
  });

  it("decodes a raw request body to text", async () => {
    // Arrange
    const body = "en=page_view&tid=G-ABC123";

    // Act
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [{ bytes: toRawBytes(body) }] } },
    ]);

    // Assert
    expect(requests[0].body).toBe(body);
  });

  it("joins multiple raw parts into one body", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: {
          raw: [{ bytes: toRawBytes("en=page_view") }, { bytes: toRawBytes("&tid=G-1") }],
        },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("en=page_view&tid=G-1");
  });

  it("decodes a multi-byte character split across two raw parts", async () => {
    // Arrange — Chrome splits large bodies at arbitrary byte offsets, which can
    // land in the middle of a UTF-8 sequence. "ö" occupies bytes 4 and 5.
    const body = "en=görüntüleme";
    const bytes = new TextEncoder().encode(body);
    const head = bytes.slice(0, 5);
    const tail = bytes.slice(5);

    // Act
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: {
          raw: [
            { bytes: head.buffer as ArrayBuffer },
            { bytes: tail.buffer as ArrayBuffer },
          ],
        },
      },
    ]);

    // Assert
    expect(requests[0].body).toBe(body);
  });

  it("decodes a multi-line raw body verbatim", async () => {
    // Arrange — GA4 batches events one per line
    const body = "en=page_view\r\nen=scroll";

    // Act
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [{ bytes: toRawBytes(body) }] } },
    ]);

    // Assert
    expect(requests[0].body).toBe(body);
  });

  it("decodes a UTF-8 raw body with non-Latin characters", async () => {
    // Arrange
    const body = "en=görüntüleme&item=決済";

    // Act
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [{ bytes: toRawBytes(body) }] } },
    ]);

    // Assert
    expect(requests[0].body).toBe(body);
  });

  it("decodes a raw body containing emoji", async () => {
    // Arrange
    const body = "en=purchase&label=🛒";

    // Act
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [{ bytes: toRawBytes(body) }] } },
    ]);

    // Assert
    expect(requests[0].body).toBe(body);
  });

  it("skips raw parts that carry no bytes", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: { raw: [{}, { bytes: toRawBytes("en=page_view") }] },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("en=page_view");
  });

  it("omits the body when every raw part lacks bytes", async () => {
    // Arrange
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [{}, {}] } },
    ]);

    // Act
    const captured = requests[0];

    // Assert
    expect(captured).not.toHaveProperty("body");
  });

  it("omits the body for an empty raw array", async () => {
    // Arrange
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [] } },
    ]);

    // Act
    const captured = requests[0];

    // Assert
    expect(captured).not.toHaveProperty("body");
  });

  it("decodes an empty raw body to no body key", async () => {
    // Arrange — a zero-length part decodes to an empty string, which is falsy
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { raw: [{ bytes: toRawBytes("") }] } },
    ]);

    // Act
    const captured = requests[0];

    // Assert
    expect(captured).not.toHaveProperty("body");
  });

  it("serializes formData into a query string body", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: { formData: { en: ["page_view"], tid: ["G-ABC123"] } },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("en=page_view&tid=G-ABC123");
  });

  it("emits one pair per value for a repeated formData key", async () => {
    // Arrange
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { formData: { en: ["a", "b"] } } },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("en=a&en=b");
  });

  it("url-encodes formData keys and values", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: { formData: { "item name": ["flat white & bun"] } },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("item%20name=flat%20white%20%26%20bun");
  });

  it("url-encodes non-Latin formData values", async () => {
    // Arrange
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { formData: { en: ["görüntüleme"] } } },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe(`en=${encodeURIComponent("görüntüleme")}`);
  });

  it("omits the body for an empty formData object", async () => {
    // Arrange
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { formData: {} } },
    ]);

    // Act
    const captured = requests[0];

    // Assert
    expect(captured).not.toHaveProperty("body");
  });

  it("omits the body when a formData key has no values", async () => {
    // Arrange
    const requests = await captureAll([
      { url: COLLECT_URL, requestBody: { formData: { en: [] } } },
    ]);

    // Act
    const captured = requests[0];

    // Assert
    expect(captured).not.toHaveProperty("body");
  });

  it("prefers raw over formData when both are present", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: {
          raw: [{ bytes: toRawBytes("from=raw") }],
          formData: { from: ["formData"] },
        },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("from=raw");
  });

  it("falls back to formData when raw is an empty array", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: { raw: [], formData: { from: ["formData"] } },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("from=formData");
  });

  it("falls back to formData when no raw part carries bytes", async () => {
    // Arrange
    const requests = await captureAll([
      {
        url: COLLECT_URL,
        requestBody: { raw: [{}], formData: { from: ["formData"] } },
      },
    ]);

    // Act
    const body = requests[0].body;

    // Assert
    expect(body).toBe("from=formData");
  });

  it("omits the body for an empty requestBody object", async () => {
    // Arrange
    const requests = await captureAll([{ url: COLLECT_URL, requestBody: {} }]);

    // Act
    const captured = requests[0];

    // Assert
    expect(captured).not.toHaveProperty("body");
  });

  it("captures an empty url verbatim", async () => {
    // Arrange — the capture does not validate urls

    // Act
    const requests = await captureAll([{ url: "" }]);

    // Assert
    expect(requests[0].url).toBe("");
  });
});

describe("createNetworkCapture — waitAndCollect", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    vi.useFakeTimers();
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("does not resolve before the wait elapses", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    const settled = vi.fn();

    // Act
    capture.waitAndCollect(WAIT_MS).then(settled);
    await vi.advanceTimersByTimeAsync(WAIT_MS - 1);

    // Assert
    expect(settled).not.toHaveBeenCalled();
  });

  it("resolves once the wait elapses", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    const settled = vi.fn();

    // Act
    capture.waitAndCollect(WAIT_MS).then(settled);
    await vi.advanceTimersByTimeAsync(WAIT_MS);

    // Assert
    expect(settled).toHaveBeenCalledTimes(1);
  });

  it("includes a late request that fired during the wait", async () => {
    // Arrange — this is the whole point of the wait window
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    const collected = capture.waitAndCollect(WAIT_MS);

    // Act
    await vi.advanceTimersByTimeAsync(WAIT_MS - 1);
    chromeMock.webRequest.onBeforeRequest.emit({ url: COLLECT_URL });
    await vi.advanceTimersByTimeAsync(1);

    // Assert
    expect(await collected).toHaveLength(1);
  });

  it("stops the listener when the wait completes", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();

    // Act
    const collected = capture.waitAndCollect(WAIT_MS);
    await vi.advanceTimersByTimeAsync(WAIT_MS);
    await collected;

    // Assert
    expect(chromeMock.webRequest.onBeforeRequest.listenerCount).toBe(0);
  });

  it("returns a copy that later requests cannot mutate", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    chromeMock.webRequest.onBeforeRequest.emit({ url: COLLECT_URL });
    const collected = capture.waitAndCollect(WAIT_MS);
    await vi.advanceTimersByTimeAsync(WAIT_MS);
    const requests = await collected;

    // Act — the listener is gone, but push directly to prove the array is detached
    capture.start();
    chromeMock.webRequest.onBeforeRequest.emit({ url: "https://late.example.com" });

    // Assert
    expect(requests).toHaveLength(1);
  });

  it("resolves immediately for a zero wait", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();

    // Act
    const collected = capture.waitAndCollect(0);
    await vi.advanceTimersByTimeAsync(0);

    // Assert
    expect(await collected).toEqual([]);
  });

  it("resolves on the next tick for a negative wait", async () => {
    // Arrange — setTimeout clamps a negative delay to 0
    const capture = createNetworkCapture(TAB_ID);
    capture.start();

    // Act
    const collected = capture.waitAndCollect(-1);
    await vi.advanceTimersByTimeAsync(0);

    // Assert
    expect(await collected).toEqual([]);
  });

  it("returns requests captured before the wait started", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    chromeMock.webRequest.onBeforeRequest.emit({ url: COLLECT_URL });

    // Act
    const collected = capture.waitAndCollect(WAIT_MS);
    await vi.advanceTimersByTimeAsync(WAIT_MS);

    // Assert
    expect(await collected).toHaveLength(1);
  });

  it("resolves even when the capture was already stopped", async () => {
    // Arrange
    const capture = createNetworkCapture(TAB_ID);
    capture.start();
    capture.stop();

    // Act
    const collected = capture.waitAndCollect(WAIT_MS);
    await vi.advanceTimersByTimeAsync(WAIT_MS);

    // Assert
    expect(await collected).toEqual([]);
  });
});
