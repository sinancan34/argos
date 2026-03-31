import { generateSelectors } from "./selector-generator";
import type { PickerResultMessage, PickerErrorMessage } from "./types";

const OVERLAY_ATTR = "data-argos-picker";
const PICKER_TIMEOUT_MS = 30_000;
const IGNORED_TAGS = new Set(["HTML", "BODY", "HEAD"]);

interface PickerState {
  overlay: HTMLDivElement;
  currentTarget: Element | null;
  timeoutId: ReturnType<typeof setTimeout>;
  abortController: AbortController;
}

function createOverlay(): HTMLDivElement {
  const overlay = document.createElement("div");
  overlay.setAttribute(OVERLAY_ATTR, "true");
  Object.assign(overlay.style, {
    position: "fixed",
    pointerEvents: "none",
    border: "2px solid #3b82f6",
    backgroundColor: "rgba(59, 130, 246, 0.1)",
    borderRadius: "2px",
    zIndex: "2147483647",
    transition: "all 0.05s ease-out",
    display: "none",
  });
  document.documentElement.appendChild(overlay);
  return overlay;
}

function positionOverlay(overlay: HTMLDivElement, element: Element): void {
  const rect = element.getBoundingClientRect();
  Object.assign(overlay.style, {
    top: `${rect.top}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    height: `${rect.height}px`,
    display: "block",
  });
}

function shouldIgnore(element: Element): boolean {
  if (IGNORED_TAGS.has(element.tagName)) return true;
  if (element.hasAttribute(OVERLAY_ATTR)) return true;
  return false;
}

function cleanup(state: PickerState): void {
  clearTimeout(state.timeoutId);
  state.abortController.abort();
  state.overlay.remove();
}

function sendResult(message: PickerResultMessage | PickerErrorMessage): void {
  chrome.runtime.sendMessage(message);
}

export function startPicker(): void {
  const abortController = new AbortController();
  const signal = abortController.signal;

  const state: PickerState = {
    overlay: createOverlay(),
    currentTarget: null,
    timeoutId: setTimeout(() => {
      cleanup(state);
      sendResult({ type: "PICKER_ERROR", error: "Picker timed out (30s)" });
    }, PICKER_TIMEOUT_MS),
    abortController,
  };

  const onMouseOver = (e: MouseEvent) => {
    const target = e.target as Element;
    if (shouldIgnore(target)) return;

    state.currentTarget = target;
    positionOverlay(state.overlay, target);
  };

  const onClick = (e: MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    const target = e.target as Element;
    if (shouldIgnore(target)) return;

    try {
      const result = generateSelectors(target);
      cleanup(state);
      sendResult({ type: "PICKER_RESULT", selectors: result });
    } catch (err: unknown) {
      cleanup(state);
      const message = err instanceof Error ? err.message : String(err);
      sendResult({ type: "PICKER_ERROR", error: message });
    }
  };

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      cleanup(state);
      sendResult({ type: "PICKER_ERROR", error: "Picker cancelled" });
    }
  };

  document.addEventListener("mouseover", onMouseOver, { capture: true, signal });
  document.addEventListener("click", onClick, { capture: true, signal });
  document.addEventListener("keydown", onKeyDown, { capture: true, signal });

  // Listen for external cancel from background
  const onMessage = (message: { type: string }) => {
    if (message.type === "PICKER_CANCEL") {
      chrome.runtime.onMessage.removeListener(onMessage);
      cleanup(state);
    }
  };
  chrome.runtime.onMessage.addListener(onMessage);

  // Also clean up if abort fires (e.g. from timeout)
  signal.addEventListener("abort", () => {
    chrome.runtime.onMessage.removeListener(onMessage);
  });
}
