// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  installChromeMock,
  uninstallChromeMock,
  type ChromeMock,
} from "@/test/chrome-mock";

const { generateSelectorsMock } = vi.hoisted(() => ({
  generateSelectorsMock: vi.fn(),
}));

vi.mock("./selector-generator", () => ({
  generateSelectors: (target: Element) => generateSelectorsMock(target),
}));

import { startPicker } from "./picker-content-script";

const OVERLAY_ATTR = "data-argos-picker";
const PICKER_TIMEOUT_MS = 30_000;
const MAX_Z_INDEX = "2147483647";

const SELECTORS = { primary: "#buy-now", alternatives: [] };
const RECT = { top: 10, left: 20, width: 100, height: 40 };

let chromeMock: ChromeMock;

function asDomRect(): DOMRect {
  return {
    ...RECT,
    x: RECT.left,
    y: RECT.top,
    right: RECT.left + RECT.width,
    bottom: RECT.top + RECT.height,
    toJSON: () => RECT,
  } as DOMRect;
}

function overlay(): HTMLElement | null {
  return document.querySelector(`[${OVERLAY_ATTR}]`);
}

/** Messages sent back through chrome.runtime.sendMessage. */
function sentMessages(): Array<{ type: string; [key: string]: unknown }> {
  return chromeMock.runtime.sendMessage.mock.calls.map(
    (call) => call[0] as { type: string },
  );
}

function createTarget(tag = "button"): HTMLElement {
  const el = document.createElement(tag);
  el.getBoundingClientRect = () => asDomRect();
  document.body.appendChild(el);
  return el;
}

function hover(target: Element): void {
  target.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
}

function click(target: Element): void {
  target.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
}

function pressKey(key: string): void {
  document.dispatchEvent(
    new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true }),
  );
}

beforeEach(() => {
  vi.useFakeTimers();
  chromeMock = installChromeMock();
  generateSelectorsMock.mockReset();
  generateSelectorsMock.mockReturnValue(SELECTORS);
  document.body.innerHTML = "";
});

afterEach(() => {
  // startPicker registers capture listeners on `document`, which outlives a single
  // test. A picker left running would intercept the next test's click via
  // stopImmediatePropagation, so cancel every active instance first — onKeyDown
  // uses stopPropagation only, so all of them see this Escape.
  pressKey("Escape");
  document
    .querySelectorAll(`[${OVERLAY_ATTR}]`)
    .forEach((element) => element.remove());

  uninstallChromeMock();
  vi.useRealTimers();
  vi.restoreAllMocks();
  document.body.innerHTML = "";
});

describe("startPicker — overlay", () => {
  it("adds an overlay element to the document", () => {
    // Arrange — nothing injected yet

    // Act
    startPicker();

    // Assert
    expect(overlay()).not.toBeNull();
  });

  it("appends the overlay to the document element, outside body", () => {
    // Arrange — body content can be replaced by the page, documentElement cannot

    // Act
    startPicker();

    // Assert
    expect(overlay()?.parentElement).toBe(document.documentElement);
  });

  it("keeps the overlay hidden until something is hovered", () => {
    // Arrange — mock configured in beforeEach

    // Act
    startPicker();

    // Assert
    expect(overlay()?.style.display).toBe("none");
  });

  it("positions the overlay fixed so it tracks the viewport", () => {
    // Arrange — mock configured in beforeEach

    // Act
    startPicker();

    // Assert
    expect(overlay()?.style.position).toBe("fixed");
  });

  it("puts the overlay at the maximum z-index", () => {
    // Arrange — it must sit above any page content

    // Act
    startPicker();

    // Assert
    expect(overlay()?.style.zIndex).toBe(MAX_Z_INDEX);
  });

  it("makes the overlay ignore pointer events", () => {
    // Arrange — otherwise it would swallow the click it is meant to observe

    // Act
    startPicker();

    // Assert
    expect(overlay()?.style.pointerEvents).toBe("none");
  });

  it("shows the overlay when an element is hovered", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    hover(target);

    // Assert
    expect(overlay()?.style.display).toBe("block");
  });

  it("positions the overlay over the hovered element", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    hover(target);

    // Assert
    expect({
      top: overlay()?.style.top,
      left: overlay()?.style.left,
      width: overlay()?.style.width,
      height: overlay()?.style.height,
    }).toEqual({
      top: `${RECT.top}px`,
      left: `${RECT.left}px`,
      width: `${RECT.width}px`,
      height: `${RECT.height}px`,
    });
  });

  it("ignores a hover on the body", () => {
    // Arrange
    startPicker();

    // Act
    hover(document.body);

    // Assert
    expect(overlay()?.style.display).toBe("none");
  });

  it("ignores a hover on the document element", () => {
    // Arrange
    startPicker();

    // Act
    hover(document.documentElement);

    // Assert
    expect(overlay()?.style.display).toBe("none");
  });

  it("ignores a hover on the overlay itself", () => {
    // Arrange
    startPicker();
    const injected = overlay() as HTMLElement;
    injected.getBoundingClientRect = () => asDomRect();

    // Act
    hover(injected);

    // Assert
    expect(injected.style.display).toBe("none");
  });

  it("repositions the overlay when a second element is hovered", () => {
    // Arrange
    startPicker();
    const first = createTarget();
    const second = createTarget("a");
    second.getBoundingClientRect = () =>
      ({ ...asDomRect(), top: 200, left: 300 }) as DOMRect;
    hover(first);

    // Act
    hover(second);

    // Assert
    expect(overlay()?.style.top).toBe("200px");
  });
});

describe("startPicker — selecting an element", () => {
  it("sends the generated selectors on click", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledWith({
      type: "PICKER_RESULT",
      selectors: SELECTORS,
    });
  });

  it("generates selectors for the clicked element", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(generateSelectorsMock).toHaveBeenCalledWith(target);
  });

  it("sends exactly one message per selection", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledTimes(1);
  });

  it("prevents the page from acting on the click", () => {
    // Arrange
    startPicker();
    const target = createTarget();
    const event = new MouseEvent("click", { bubbles: true, cancelable: true });

    // Act
    target.dispatchEvent(event);

    // Assert
    expect(event.defaultPrevented).toBe(true);
  });

  it("keeps the click from reaching a page listener", () => {
    // Arrange — the picker captures before the page sees the event
    startPicker();
    const target = createTarget();
    const pageListener = vi.fn();
    target.addEventListener("click", pageListener);

    // Act
    click(target);

    // Assert
    expect(pageListener).not.toHaveBeenCalled();
  });

  it("removes the overlay after a selection", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(overlay()).toBeNull();
  });

  it("stops tracking hovers after a selection", () => {
    // Arrange
    startPicker();
    const target = createTarget();
    click(target);

    // Act
    hover(target);

    // Assert
    expect(overlay()).toBeNull();
  });

  it("ignores a click on the body", () => {
    // Arrange
    startPicker();

    // Act
    click(document.body);

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("keeps the overlay alive after an ignored click", () => {
    // Arrange
    startPicker();

    // Act
    click(document.body);

    // Assert
    expect(overlay()).not.toBeNull();
  });

  it("sends an error when selector generation throws", () => {
    // Arrange
    generateSelectorsMock.mockImplementation(() => {
      throw new Error("finder exploded");
    });
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledWith({
      type: "PICKER_ERROR",
      error: "finder exploded",
    });
  });

  it("stringifies a non-Error thrown during generation", () => {
    // Arrange
    generateSelectorsMock.mockImplementation(() => {
      throw "string failure";
    });
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(sentMessages()[0].error).toBe("string failure");
  });

  it("removes the overlay when generation throws", () => {
    // Arrange
    generateSelectorsMock.mockImplementation(() => {
      throw new Error("finder exploded");
    });
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(overlay()).toBeNull();
  });
});

describe("startPicker — cancellation", () => {
  it("reports a cancellation when Escape is pressed", () => {
    // Arrange
    startPicker();

    // Act
    pressKey("Escape");

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledWith({
      type: "PICKER_ERROR",
      error: "Picker cancelled",
    });
  });

  it("removes the overlay when Escape is pressed", () => {
    // Arrange
    startPicker();

    // Act
    pressKey("Escape");

    // Assert
    expect(overlay()).toBeNull();
  });

  it("ignores other keys", () => {
    // Arrange
    startPicker();

    // Act
    pressKey("Enter");

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("keeps the overlay alive for other keys", () => {
    // Arrange
    startPicker();

    // Act
    pressKey("a");

    // Assert
    expect(overlay()).not.toBeNull();
  });

  it("reports a timeout after 30 seconds", async () => {
    // Arrange
    startPicker();

    // Act
    await vi.advanceTimersByTimeAsync(PICKER_TIMEOUT_MS);

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledWith({
      type: "PICKER_ERROR",
      error: "Picker timed out (30s)",
    });
  });

  it("does not time out just before 30 seconds", async () => {
    // Arrange
    startPicker();

    // Act
    await vi.advanceTimersByTimeAsync(PICKER_TIMEOUT_MS - 1);

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("removes the overlay on timeout", async () => {
    // Arrange
    startPicker();

    // Act
    await vi.advanceTimersByTimeAsync(PICKER_TIMEOUT_MS);

    // Assert
    expect(overlay()).toBeNull();
  });

  it("does not time out after a selection", async () => {
    // Arrange
    startPicker();
    const target = createTarget();
    click(target);

    // Act
    await vi.advanceTimersByTimeAsync(PICKER_TIMEOUT_MS);

    // Assert
    expect(sentMessages().map((message) => message.type)).toEqual([
      "PICKER_RESULT",
    ]);
  });

  it("does not time out after an Escape cancellation", async () => {
    // Arrange
    startPicker();
    pressKey("Escape");

    // Act
    await vi.advanceTimersByTimeAsync(PICKER_TIMEOUT_MS);

    // Assert
    expect(sentMessages()).toHaveLength(1);
  });

  it("removes the overlay on an external PICKER_CANCEL", () => {
    // Arrange
    startPicker();

    // Act
    chromeMock.runtime.onMessage.emit({ type: "PICKER_CANCEL" }, {});

    // Assert
    expect(overlay()).toBeNull();
  });

  it("sends no message for an external PICKER_CANCEL", () => {
    // Arrange — the background already knows it cancelled
    startPicker();

    // Act
    chromeMock.runtime.onMessage.emit({ type: "PICKER_CANCEL" }, {});

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("ignores an unrelated runtime message", () => {
    // Arrange
    startPicker();

    // Act
    chromeMock.runtime.onMessage.emit({ type: "SOMETHING_ELSE" }, {});

    // Assert
    expect(overlay()).not.toBeNull();
  });

  it("unregisters its runtime message listener after a selection", () => {
    // Arrange
    startPicker();
    const target = createTarget();

    // Act
    click(target);

    // Assert
    expect(chromeMock.runtime.onMessage.listenerCount).toBe(0);
  });

  it("unregisters its runtime message listener on timeout", async () => {
    // Arrange
    startPicker();

    // Act
    await vi.advanceTimersByTimeAsync(PICKER_TIMEOUT_MS);

    // Assert
    expect(chromeMock.runtime.onMessage.listenerCount).toBe(0);
  });

  it("stops tracking hovers after an Escape cancellation", () => {
    // Arrange
    startPicker();
    const target = createTarget();
    pressKey("Escape");

    // Act
    hover(target);

    // Assert
    expect(overlay()).toBeNull();
  });

  it("prevents the page from acting on the Escape key", () => {
    // Arrange
    startPicker();
    const event = new KeyboardEvent("keydown", {
      key: "Escape",
      bubbles: true,
      cancelable: true,
    });

    // Act
    document.dispatchEvent(event);

    // Assert
    expect(event.defaultPrevented).toBe(true);
  });
});
