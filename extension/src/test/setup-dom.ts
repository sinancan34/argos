// Global test setup: jest-dom matchers plus the browser APIs Radix UI primitives
// expect but jsdom does not implement. Guarded so it stays inert for the
// node-environment test files (this file runs for every test).

import "@testing-library/jest-dom/vitest";

if (typeof window !== "undefined") {
  // Radix uses ResizeObserver for positioning; jsdom has no implementation.
  if (!("ResizeObserver" in globalThis)) {
    class ResizeObserverStub {
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    }
    (globalThis as unknown as { ResizeObserver: unknown }).ResizeObserver =
      ResizeObserverStub;
  }

  if (!("DOMRect" in globalThis)) {
    (globalThis as unknown as { DOMRect: unknown }).DOMRect = class {
      constructor(
        readonly x = 0,
        readonly y = 0,
        readonly width = 0,
        readonly height = 0,
      ) {}
      get top() {
        return this.y;
      }
      get left() {
        return this.x;
      }
      get right() {
        return this.x + this.width;
      }
      get bottom() {
        return this.y + this.height;
      }
    };
  }

  // Pointer capture and scrolling are used by Radix Select/DropdownMenu on
  // pointer interactions; jsdom implements none of them.
  const elementStubs: Record<string, unknown> = {
    hasPointerCapture: () => false,
    setPointerCapture: () => undefined,
    releasePointerCapture: () => undefined,
    scrollIntoView: () => undefined,
  };

  for (const [name, implementation] of Object.entries(elementStubs)) {
    if (!(name in Element.prototype)) {
      Object.defineProperty(Element.prototype, name, {
        value: implementation,
        writable: true,
        configurable: true,
      });
    }
  }
}
