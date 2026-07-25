// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, cleanup } from "@testing-library/react";
import {
  installChromeMock,
  uninstallChromeMock,
  type ChromeMock,
} from "@/test/chrome-mock";
import { useElementPicker } from "./use-element-picker";
import type { PickerSelectorResult } from "@/lib/picker/types";

const INSPECTED_TAB_ID = 11;
const SELECTORS: PickerSelectorResult = {
  primary: "#buy-now",
  alternatives: [],
};

let chromeMock: ChromeMock;

/** Pretends the hook is running inside a DevTools panel for the given tab. */
function withInspectedTab(tabId: unknown = INSPECTED_TAB_ID): void {
  chromeMock.devtools = { inspectedWindow: { tabId } };
}

/** Messages the hook sent through chrome.runtime.sendMessage. */
function sentMessages(): Array<{ type: string; [key: string]: unknown }> {
  return chromeMock.runtime.sendMessage.mock.calls.map(
    (call) => call[0] as { type: string },
  );
}

/** Delivers a runtime message to the hook's listener. */
function deliver(message: Record<string, unknown>): void {
  act(() => {
    chromeMock.runtime.onMessage.emit(message as { type: string }, {});
  });
}

async function flush(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

describe("useElementPicker", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    chromeMock.runtime.sendMessage.mockResolvedValue({ success: true });
  });

  afterEach(() => {
    cleanup();
    uninstallChromeMock();
    vi.restoreAllMocks();
  });

  it("starts idle", () => {
    // Arrange & Act
    const { result } = renderHook(() => useElementPicker());

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("does nothing outside a DevTools page", () => {
    // Arrange — chrome.devtools is absent
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("stays idle when there is no inspected tab", () => {
    // Arrange
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("does nothing when the inspected tab id is not a number", () => {
    // Arrange
    withInspectedTab("11");
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("asks the background to start on the inspected tab", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledWith({
      type: "PICKER_START",
      tabId: INSPECTED_TAB_ID,
    });
  });

  it("reports that picking is active", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(result.current.isPicking).toBe(true);
  });

  it("registers a listener for the picker's reply", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(chromeMock.runtime.onMessage.listenerCount).toBe(1);
  });

  it("accepts tab id 0", () => {
    // Arrange
    withInspectedTab(0);
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledWith({
      type: "PICKER_START",
      tabId: 0,
    });
  });

  it("ignores a second start while already picking", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(chromeMock.runtime.sendMessage).toHaveBeenCalledTimes(1);
  });

  it("delivers the picked selectors to the callback", () => {
    // Arrange
    withInspectedTab();
    const onResult = vi.fn();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(onResult));

    // Act
    deliver({ type: "PICKER_RESULT", selectors: SELECTORS });

    // Assert
    expect(onResult).toHaveBeenCalledWith(SELECTORS);
  });

  it("returns to idle after a result", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    deliver({ type: "PICKER_RESULT", selectors: SELECTORS });

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("unregisters its listener after a result", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    deliver({ type: "PICKER_RESULT", selectors: SELECTORS });

    // Assert
    expect(chromeMock.runtime.onMessage.listenerCount).toBe(0);
  });

  it("ignores a result that carries no selectors", () => {
    // Arrange
    withInspectedTab();
    const onResult = vi.fn();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(onResult));

    // Act
    deliver({ type: "PICKER_RESULT" });

    // Assert
    expect(onResult).not.toHaveBeenCalled();
  });

  it("keeps picking after a result with no selectors", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    deliver({ type: "PICKER_RESULT" });

    // Assert
    expect(result.current.isPicking).toBe(true);
  });

  it("returns to idle on a picker error", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    deliver({ type: "PICKER_ERROR", error: "Picker cancelled" });

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("does not invoke the callback on a picker error", () => {
    // Arrange
    withInspectedTab();
    const onResult = vi.fn();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(onResult));

    // Act
    deliver({ type: "PICKER_ERROR", error: "Picker timed out (30s)" });

    // Assert
    expect(onResult).not.toHaveBeenCalled();
  });

  it("ignores an unrelated runtime message", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    deliver({ type: "SOMETHING_ELSE" });

    // Assert
    expect(result.current.isPicking).toBe(true);
  });

  it("gives up when the background refuses to start", async () => {
    // Arrange — another operation already holds the slot
    withInspectedTab();
    chromeMock.runtime.sendMessage.mockResolvedValue({
      success: false,
      error: "Another operation is in progress",
    });
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));
    await flush();

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("keeps picking when the background confirms the start", async () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));
    await flush();

    // Assert
    expect(result.current.isPicking).toBe(true);
  });

  it("keeps picking when the background sends no response", async () => {
    // Arrange — an undefined reply is not a refusal
    withInspectedTab();
    chromeMock.runtime.sendMessage.mockResolvedValue(undefined);
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.startPicker(vi.fn()));
    await flush();

    // Assert
    expect(result.current.isPicking).toBe(true);
  });

  it("asks the background to cancel", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    act(() => result.current.cancelPicker());

    // Assert
    expect(sentMessages()).toContainEqual({ type: "PICKER_CANCEL" });
  });

  it("returns to idle after cancelling", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    act(() => result.current.cancelPicker());

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("ignores a cancel when nothing is being picked", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());

    // Act
    act(() => result.current.cancelPicker());

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("swallows a failure to deliver the cancel", async () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));
    chromeMock.runtime.sendMessage.mockRejectedValue(new Error("No receiver"));

    // Act
    act(() => result.current.cancelPicker());
    await flush();

    // Assert
    expect(result.current.isPicking).toBe(false);
  });

  it("cancels an active picker on unmount", () => {
    // Arrange — otherwise the overlay would outlive the panel
    withInspectedTab();
    const { result, unmount } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));
    chromeMock.runtime.sendMessage.mockClear();

    // Act
    unmount();

    // Assert
    expect(sentMessages()).toContainEqual({ type: "PICKER_CANCEL" });
  });

  it("sends nothing on unmount when idle", () => {
    // Arrange
    withInspectedTab();
    const { unmount } = renderHook(() => useElementPicker());

    // Act
    unmount();

    // Assert
    expect(chromeMock.runtime.sendMessage).not.toHaveBeenCalled();
  });

  it("leaves no listener behind on unmount", () => {
    // Arrange
    withInspectedTab();
    const { result, unmount } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));

    // Act
    unmount();

    // Assert
    expect(chromeMock.runtime.onMessage.listenerCount).toBe(0);
  });

  it("allows a fresh pick after one completes", () => {
    // Arrange
    withInspectedTab();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(vi.fn()));
    deliver({ type: "PICKER_RESULT", selectors: SELECTORS });

    // Act
    act(() => result.current.startPicker(vi.fn()));

    // Assert
    expect(result.current.isPicking).toBe(true);
  });

  it("routes a second pick's result to the newer callback", () => {
    // Arrange
    withInspectedTab();
    const first = vi.fn();
    const second = vi.fn();
    const { result } = renderHook(() => useElementPicker());
    act(() => result.current.startPicker(first));
    deliver({ type: "PICKER_RESULT", selectors: SELECTORS });
    act(() => result.current.startPicker(second));

    // Act
    deliver({ type: "PICKER_RESULT", selectors: SELECTORS });

    // Assert
    expect(second).toHaveBeenCalledTimes(1);
  });
});
