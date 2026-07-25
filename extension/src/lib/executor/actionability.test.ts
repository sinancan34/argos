// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { waitForActionable } from "./actionability";

const TIMEOUT = 5000;
// Enough fake time for the requestAnimationFrame loop to walk
// visibility → stability → clickability (4 frames at ~16ms).
const FRAMES_MS = 200;
const PAST_DEADLINE_MS = TIMEOUT + 100;

const SELECTOR = "#target";
const RECT = { top: 10, left: 20, width: 100, height: 40 };

const NOT_FOUND_ERROR = `Element not found in DOM within timeout: ${SELECTOR}`;
const NOT_VISIBLE_ERROR = "Element found but not visible within timeout";
const NOT_STABLE_ERROR = "Element not stable (still animating) within timeout";
const OBSTRUCTED_ERROR = "Element obstructed by another element within timeout";

interface PlainRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

function asDomRect(rect: PlainRect): DOMRect {
  return {
    ...rect,
    x: rect.left,
    y: rect.top,
    right: rect.left + rect.width,
    bottom: rect.top + rect.height,
    toJSON: () => rect,
  } as DOMRect;
}

/** Stubs the layout-dependent APIs jsdom does not implement. */
function stubRect(el: HTMLElement, rect: PlainRect = RECT): void {
  el.getBoundingClientRect = () => asDomRect(rect);
}

/** Makes getBoundingClientRect report a new position on every call. */
function stubMovingRect(el: HTMLElement): void {
  let top = 0;
  el.getBoundingClientRect = () => asDomRect({ ...RECT, top: top++ });
}

/** Declares which element sits at the hit-test point. */
function stubTopElement(el: Element | null): void {
  document.elementFromPoint = (() => el) as typeof document.elementFromPoint;
}

function createTarget(id = "target"): HTMLElement {
  const el = document.createElement("div");
  el.id = id;
  // position:fixed satisfies isVisible's offsetParent gate, which jsdom always
  // reports as null regardless of layout.
  el.style.position = "fixed";
  el.scrollIntoView = vi.fn();
  stubRect(el);
  return el;
}

/** A target that is present, visible, stable, and unobstructed. */
function mountActionable(): HTMLElement {
  const el = createTarget();
  document.body.appendChild(el);
  stubTopElement(el);
  return el;
}

/**
 * Starts a wait and attaches a no-op catch so a rejection that lands while fake
 * timers are being advanced is never reported as an unhandled rejection. The
 * returned promise is still the one under test.
 */
function startWait(selector: string, timeout: number): Promise<HTMLElement> {
  const promise = waitForActionable(selector, timeout);
  promise.catch(() => undefined);
  return promise;
}

describe("waitForActionable", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = "";
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    document.body.innerHTML = "";
  });

  describe("DOM presence", () => {
    it("resolves with the element when it is already actionable", async () => {
      // Arrange
      const el = mountActionable();

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("waits for an element added to the DOM later", async () => {
      // Arrange — nothing matches the selector yet
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(10);

      // Act
      const el = createTarget();
      document.body.appendChild(el);
      stubTopElement(el);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("finds an element added deep inside a new subtree", async () => {
      // Arrange — the observer watches the whole subtree
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(10);

      // Act
      const wrapper = document.createElement("section");
      const el = createTarget();
      wrapper.appendChild(el);
      document.body.appendChild(wrapper);
      stubTopElement(el);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("rejects when the element never appears", async () => {
      // Arrange — empty document body

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_FOUND_ERROR);
    });

    it("names the selector in the not-found error", async () => {
      // Arrange
      const missingSelector = ".no-such-class";

      // Act
      const promise = startWait(missingSelector, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(
        `Element not found in DOM within timeout: ${missingSelector}`,
      );
    });

    it("treats a non-HTMLElement match as absent", async () => {
      // Arrange — an SVG element is an Element but not an HTMLElement
      const svg = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "svg",
      );
      svg.id = "target";
      document.body.appendChild(svg);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_FOUND_ERROR);
    });

    it("resolves with the first match when the selector is ambiguous", async () => {
      // Arrange
      const first = createTarget();
      first.className = "shared";
      const second = createTarget("other");
      second.className = "shared";
      document.body.append(first, second);
      stubTopElement(first);

      // Act
      const promise = startWait(".shared", TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(first);
    });

    it("rejects immediately for a zero timeout when the element is absent", async () => {
      // Arrange — the deadline has already passed

      // Act
      const promise = startWait(SELECTOR, 0);
      await vi.advanceTimersByTimeAsync(1);

      // Assert
      await expect(promise).rejects.toThrow(NOT_FOUND_ERROR);
    });

    it("rejects for a negative timeout when the element is absent", async () => {
      // Arrange — Math.max clamps the wait to 0

      // Act
      const promise = startWait(SELECTOR, -1000);
      await vi.advanceTimersByTimeAsync(1);

      // Assert
      await expect(promise).rejects.toThrow(NOT_FOUND_ERROR);
    });

    // querySelector throws synchronously for a malformed selector, and the first
    // call happens before the promise chain is built — so waitForActionable throws
    // rather than returning a rejected promise. The content script's handleClick
    // awaits it inside try/catch, so the throw still surfaces as a step error.
    it("throws synchronously on a malformed selector", () => {
      // Arrange — ":::" is not parseable CSS

      // Act & Assert
      expect(() => waitForActionable(":::", TIMEOUT)).toThrow(
        /Invalid selector/,
      );
    });
  });

  describe("visibility", () => {
    it("rejects when the element has display none", async () => {
      // Arrange
      const el = mountActionable();
      el.style.display = "none";

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_VISIBLE_ERROR);
    });

    it("rejects when the element has visibility hidden", async () => {
      // Arrange
      const el = mountActionable();
      el.style.visibility = "hidden";

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_VISIBLE_ERROR);
    });

    it("rejects when the element is fully transparent", async () => {
      // Arrange
      const el = mountActionable();
      el.style.opacity = "0";

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_VISIBLE_ERROR);
    });

    it("accepts a partially transparent element", async () => {
      // Arrange — only a computed opacity of exactly 0 blocks the click
      const el = mountActionable();
      el.style.opacity = "0.01";

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("resolves once a hidden element becomes visible", async () => {
      // Arrange
      const el = mountActionable();
      el.style.visibility = "hidden";
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(50);

      // Act
      el.style.visibility = "visible";
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("scrolls the element into view once it is visible", async () => {
      // Arrange
      const el = mountActionable();

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);
      await promise;

      // Assert
      expect(el.scrollIntoView).toHaveBeenCalledWith({
        block: "center",
        behavior: "instant",
      });
    });

    it("does not scroll an element that never becomes visible", async () => {
      // Arrange
      const el = mountActionable();
      el.style.display = "none";

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);
      await promise.catch(() => undefined);

      // Assert
      expect(el.scrollIntoView).not.toHaveBeenCalled();
    });

    it("scrolls only once across the whole wait", async () => {
      // Arrange
      const el = mountActionable();

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);
      await promise;

      // Assert
      expect(el.scrollIntoView).toHaveBeenCalledTimes(1);
    });
  });

  describe("stability", () => {
    it("rejects when the element keeps moving", async () => {
      // Arrange — an element mid-animation reports a new rect every frame
      const el = mountActionable();
      stubMovingRect(el);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_STABLE_ERROR);
    });

    it("resolves once a moving element settles", async () => {
      // Arrange
      const el = mountActionable();
      stubMovingRect(el);
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(100);

      // Act — freeze the rect
      stubRect(el);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("treats a zero-size rect as stable", async () => {
      // Arrange — an unstyled element still has a consistent rect
      const el = mountActionable();
      stubRect(el, { top: 0, left: 0, width: 0, height: 0 });
      stubTopElement(el);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("treats a size change alone as unstable", async () => {
      // Arrange — position fixed, dimensions growing
      const el = mountActionable();
      let width = 10;
      el.getBoundingClientRect = () =>
        asDomRect({ ...RECT, width: width++ });

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_STABLE_ERROR);
    });
  });

  describe("clickability", () => {
    it("resolves when the element itself is on top", async () => {
      // Arrange
      const el = mountActionable();

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("resolves when a descendant is on top", async () => {
      // Arrange — clicking a button's inner label still hits the button
      const el = mountActionable();
      const child = document.createElement("span");
      el.appendChild(child);
      stubTopElement(child);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("rejects when another element covers the center point", async () => {
      // Arrange — e.g. a cookie banner overlay
      mountActionable();
      const overlay = document.createElement("div");
      document.body.appendChild(overlay);
      stubTopElement(overlay);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(OBSTRUCTED_ERROR);
    });

    it("rejects when the hit test finds nothing", async () => {
      // Arrange — the center point is outside the viewport
      mountActionable();
      stubTopElement(null);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(OBSTRUCTED_ERROR);
    });

    it("resolves once an obstruction is removed", async () => {
      // Arrange
      const el = mountActionable();
      const overlay = document.createElement("div");
      document.body.appendChild(overlay);
      stubTopElement(overlay);
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(100);

      // Act
      stubTopElement(el);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);

      // Assert
      await expect(promise).resolves.toBe(el);
    });

    it("hit-tests the center of the element's rect", async () => {
      // Arrange
      const el = mountActionable();
      const hitTest = vi.fn(() => el);
      document.elementFromPoint = hitTest as typeof document.elementFromPoint;

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(FRAMES_MS);
      await promise;

      // Assert
      expect(hitTest).toHaveBeenCalledWith(
        RECT.left + RECT.width / 2,
        RECT.top + RECT.height / 2,
      );
    });
  });

  describe("phase reporting", () => {
    it("reports the visibility phase when the element is present but hidden", async () => {
      // Arrange — the error names the phase the wait was stuck in
      const el = mountActionable();
      el.style.display = "none";

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_VISIBLE_ERROR);
    });

    it("reports the stability phase once visibility has passed", async () => {
      // Arrange
      const el = mountActionable();
      stubMovingRect(el);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(NOT_STABLE_ERROR);
    });

    it("reports the clickability phase once stability has passed", async () => {
      // Arrange
      mountActionable();
      stubTopElement(null);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toThrow(OBSTRUCTED_ERROR);
    });

    it("rejects with an Error instance", async () => {
      // Arrange
      mountActionable();
      stubTopElement(null);

      // Act
      const promise = startWait(SELECTOR, TIMEOUT);
      await vi.advanceTimersByTimeAsync(PAST_DEADLINE_MS);

      // Assert
      await expect(promise).rejects.toBeInstanceOf(Error);
    });
  });
});
