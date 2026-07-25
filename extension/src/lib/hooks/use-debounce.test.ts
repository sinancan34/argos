// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, cleanup, act } from "@testing-library/react";
import { useDebounce } from "./use-debounce";

const DELAY = 300;
const LONG_STRING_LENGTH = 10000;

/** Advances fake timers inside act() so React can flush the resulting state update. */
function advance(ms: number): void {
  act(() => {
    vi.advanceTimersByTime(ms);
  });
}

describe("useDebounce", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    cleanup();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("returns the initial value synchronously", () => {
    // Arrange & Act
    const { result } = renderHook(() => useDebounce("initial", DELAY));

    // Assert
    expect(result.current).toBe("initial");
  });

  it("still returns the previous value just before the delay elapses", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "second" });
    advance(DELAY - 1);

    // Assert
    expect(result.current).toBe("first");
  });

  it("returns the new value once the delay elapses", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "second" });
    advance(DELAY);

    // Assert
    expect(result.current).toBe("second");
  });

  it("emits only the final value when the input changes rapidly", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "a" } },
    );

    // Act — each change restarts the timer before it can fire
    rerender({ value: "ab" });
    advance(DELAY - 100);
    rerender({ value: "abc" });
    advance(DELAY - 100);
    rerender({ value: "abcd" });
    advance(DELAY);

    // Assert
    expect(result.current).toBe("abcd");
  });

  it("never exposes an intermediate value from a rapid change sequence", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "a" } },
    );

    // Act
    rerender({ value: "ab" });
    advance(DELAY - 1);
    rerender({ value: "abc" });
    advance(DELAY - 1);

    // Assert — still the original, because neither timer completed
    expect(result.current).toBe("a");
  });

  it("settles on a value that is set back to the original", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "second" });
    advance(DELAY);
    rerender({ value: "first" });
    advance(DELAY);

    // Assert
    expect(result.current).toBe("first");
  });

  it("updates on the next tick when the delay is zero", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 0),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "second" });
    advance(0);

    // Assert
    expect(result.current).toBe("second");
  });

  it("updates immediately on the next tick for a negative delay", () => {
    // Arrange — setTimeout clamps negative delays to 0
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, -1),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "second" });
    advance(0);

    // Assert
    expect(result.current).toBe("second");
  });

  it("updates on the next tick when the delay is NaN", () => {
    // Arrange — setTimeout treats NaN as 0
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, NaN),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "second" });
    advance(0);

    // Assert
    expect(result.current).toBe("second");
  });

  it("restarts the timer when the delay changes mid-flight", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "first", delay: DELAY } },
    );

    // Act — changing delay re-runs the effect, discarding the elapsed time
    rerender({ value: "second", delay: DELAY });
    advance(DELAY - 50);
    rerender({ value: "second", delay: DELAY * 2 });
    advance(DELAY - 50);

    // Assert
    expect(result.current).toBe("first");
  });

  it("applies a shortened delay to the pending value", () => {
    // Arrange
    const shortDelay = 10;
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "first", delay: DELAY } },
    );

    // Act
    rerender({ value: "second", delay: shortDelay });
    advance(shortDelay);

    // Assert
    expect(result.current).toBe("second");
  });

  it("debounces a number value", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: 1 } },
    );

    // Act
    rerender({ value: 2 });
    advance(DELAY);

    // Assert
    expect(result.current).toBe(2);
  });

  it("debounces a zero value rather than treating it as absent", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: 1 } },
    );

    // Act
    rerender({ value: 0 });
    advance(DELAY);

    // Assert
    expect(result.current).toBe(0);
  });

  it("debounces a boolean value", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: false } },
    );

    // Act
    rerender({ value: true });
    advance(DELAY);

    // Assert
    expect(result.current).toBe(true);
  });

  it("debounces an undefined value", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" as string | undefined } },
    );

    // Act
    rerender({ value: undefined });
    advance(DELAY);

    // Assert
    expect(result.current).toBeUndefined();
  });

  it("debounces a null value", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" as string | null } },
    );

    // Act
    rerender({ value: null });
    advance(DELAY);

    // Assert
    expect(result.current).toBeNull();
  });

  it("debounces an empty string", () => {
    // Arrange
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" } },
    );

    // Act
    rerender({ value: "" });
    advance(DELAY);

    // Assert
    expect(result.current).toBe("");
  });

  it("preserves object identity for an object value", () => {
    // Arrange
    const next = { name: "checkout" };
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: { name: "initial" } } },
    );

    // Act
    rerender({ value: next });
    advance(DELAY);

    // Assert
    expect(result.current).toBe(next);
  });

  it("re-runs the effect for a new object with identical contents", () => {
    // Arrange — the effect depends on reference identity, not deep equality
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: { name: "same" } } },
    );
    const replacement = { name: "same" };

    // Act
    rerender({ value: replacement });
    advance(DELAY);

    // Assert
    expect(result.current).toBe(replacement);
  });

  it("debounces an array value", () => {
    // Arrange
    const next = ["a", "b"];
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: [] as string[] } },
    );

    // Act
    rerender({ value: next });
    advance(DELAY);

    // Assert
    expect(result.current).toEqual(["a", "b"]);
  });

  it("debounces a very long string", () => {
    // Arrange
    const longValue = "a".repeat(LONG_STRING_LENGTH);
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "" } },
    );

    // Act
    rerender({ value: longValue });
    advance(DELAY);

    // Assert
    expect(result.current).toHaveLength(LONG_STRING_LENGTH);
  });

  it("debounces a Turkish search term", () => {
    // Arrange
    const turkishTerm = "ödeme akışı";
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "" } },
    );

    // Act
    rerender({ value: turkishTerm });
    advance(DELAY);

    // Assert
    expect(result.current).toBe(turkishTerm);
  });

  it("clears the pending timeout on unmount", () => {
    // Arrange
    const clearSpy = vi.spyOn(globalThis, "clearTimeout");
    const { rerender, unmount } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" } },
    );
    rerender({ value: "second" });
    clearSpy.mockClear();

    // Act
    unmount();

    // Assert
    expect(clearSpy).toHaveBeenCalled();
  });

  it("leaves no timer pending after unmount", () => {
    // Arrange
    const { rerender, unmount } = renderHook(
      ({ value }) => useDebounce(value, DELAY),
      { initialProps: { value: "first" } },
    );
    rerender({ value: "second" });

    // Act
    unmount();

    // Assert
    expect(vi.getTimerCount()).toBe(0);
  });

  it("schedules exactly one timer per value change", () => {
    // Arrange
    const { rerender } = renderHook(({ value }) => useDebounce(value, DELAY), {
      initialProps: { value: "first" },
    });

    // Act
    rerender({ value: "second" });
    rerender({ value: "third" });

    // Assert — the previous timer is cleared before the next is set
    expect(vi.getTimerCount()).toBe(1);
  });

  it("does not schedule a timer when the value is unchanged across a rerender", () => {
    // Arrange
    const { rerender } = renderHook(({ value }) => useDebounce(value, DELAY), {
      initialProps: { value: "first" },
    });
    advance(DELAY);

    // Act — same value and delay, so the effect does not re-run
    rerender({ value: "first" });

    // Assert
    expect(vi.getTimerCount()).toBe(0);
  });
});
