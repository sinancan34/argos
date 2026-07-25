// Shared chrome.* test double for the background execution layer.
//
// The extension talks to Chrome through a handful of namespaces (tabs, scripting,
// webNavigation, webRequest, runtime, debugger). Real ones do not exist under
// vitest, so `installChromeMock()` puts a structural fake on globalThis and hands
// back typed handles for driving it: vi.fn() methods to assert on, and FakeEvent
// instances whose `emit` synchronously invokes whatever the code under test
// registered.

import { vi, type Mock } from "vitest";

type Listener<TArgs extends readonly unknown[]> = (...args: TArgs) => unknown;

/** Minimal stand-in for a chrome.events.Event, with a test-only `emit`. */
export class FakeEvent<TArgs extends readonly unknown[]> {
  private listeners: ReadonlyArray<Listener<TArgs>> = [];

  addListener = (listener: Listener<TArgs>): void => {
    this.listeners = [...this.listeners, listener];
  };

  removeListener = (listener: Listener<TArgs>): void => {
    this.listeners = this.listeners.filter((l) => l !== listener);
  };

  hasListener = (listener: Listener<TArgs>): boolean =>
    this.listeners.includes(listener);

  /** Number of currently registered listeners — asserts cleanup happened. */
  get listenerCount(): number {
    return this.listeners.length;
  }

  /** Synchronously invokes every listener over a snapshot of the list. */
  emit(...args: TArgs): void {
    for (const listener of [...this.listeners]) {
      listener(...args);
    }
  }
}

export interface TabRemovedInfo {
  windowId: number;
  isWindowClosing: boolean;
}

export interface NavigationDetails {
  tabId: number;
  frameId: number;
  url?: string;
}

export interface NavigationErrorDetails extends NavigationDetails {
  error: string;
}

export interface MessageSender {
  tab?: { id?: number };
}

export interface WebRequestRawPart {
  bytes?: ArrayBuffer;
}

export interface WebRequestBody {
  raw?: WebRequestRawPart[];
  formData?: Record<string, string[]>;
  error?: string;
}

export interface WebRequestDetails {
  url: string;
  method?: string;
  requestBody?: WebRequestBody;
}

export interface WebRequestFilter {
  urls: string[];
  tabId?: number;
}

export interface ChromeMock {
  tabs: {
    create: Mock;
    update: Mock;
    remove: Mock;
    sendMessage: Mock;
    onRemoved: FakeEvent<[number, TabRemovedInfo]>;
  };
  scripting: {
    executeScript: Mock;
  };
  webNavigation: {
    onDOMContentLoaded: FakeEvent<[NavigationDetails]>;
    onErrorOccurred: FakeEvent<[NavigationErrorDetails]>;
  };
  webRequest: {
    onBeforeRequest: {
      addListener: Mock;
      removeListener: Mock;
      /** Invokes every listener registered via addListener. */
      emit: (details: WebRequestDetails) => void;
      readonly listenerCount: number;
    };
  };
  runtime: {
    connect: Mock;
    sendMessage: Mock;
    onMessage: FakeEvent<
      [{ type: string; [key: string]: unknown }, MessageSender, Mock?]
    >;
    onConnect: FakeEvent<[PortMock]>;
    lastError: { message: string } | undefined;
  };
  debugger: {
    attach: Mock;
    detach: Mock;
    sendCommand: Mock;
  };
  /**
   * Only defined inside a DevTools page. Left absent by install() so the
   * "no inspected tab" path is the default; assign it to simulate the panel.
   */
  devtools?: { inspectedWindow?: { tabId?: unknown } };
}

/**
 * A chrome.webRequest.onBeforeRequest double. Unlike the other events this one
 * needs vi.fn() add/removeListener so tests can assert on the filter and the
 * extraInfoSpec arguments, so it does not reuse FakeEvent directly.
 */
function createWebRequestEvent(): ChromeMock["webRequest"]["onBeforeRequest"] {
  let listeners: ReadonlyArray<(details: WebRequestDetails) => void> = [];

  const addListener = vi.fn((listener: (details: WebRequestDetails) => void) => {
    listeners = [...listeners, listener];
  });

  const removeListener = vi.fn(
    (listener: (details: WebRequestDetails) => void) => {
      listeners = listeners.filter((l) => l !== listener);
    },
  );

  return {
    addListener,
    removeListener,
    emit: (details: WebRequestDetails) => {
      for (const listener of [...listeners]) listener(details);
    },
    get listenerCount() {
      return listeners.length;
    },
  };
}

/** A chrome.runtime.Port double for the panel↔background execution port. */
export interface PortMock {
  name: string;
  postMessage: Mock;
  disconnect: Mock;
  onMessage: FakeEvent<[unknown]>;
  onDisconnect: FakeEvent<[]>;
}

export function createPortMock(name = "argos-execution"): PortMock {
  return {
    name,
    postMessage: vi.fn(),
    disconnect: vi.fn(),
    onMessage: new FakeEvent<[unknown]>(),
    onDisconnect: new FakeEvent<[]>(),
  };
}

/**
 * Installs the fake on globalThis.chrome and returns handles to drive it.
 * Call `uninstallChromeMock()` in afterEach to avoid leaking between files.
 */
export function installChromeMock(): ChromeMock {
  const mock: ChromeMock = {
    tabs: {
      create: vi.fn(),
      update: vi.fn(),
      remove: vi.fn(),
      sendMessage: vi.fn(),
      onRemoved: new FakeEvent<[number, TabRemovedInfo]>(),
    },
    scripting: {
      executeScript: vi.fn(),
    },
    webNavigation: {
      onDOMContentLoaded: new FakeEvent<[NavigationDetails]>(),
      onErrorOccurred: new FakeEvent<[NavigationErrorDetails]>(),
    },
    webRequest: {
      onBeforeRequest: createWebRequestEvent(),
    },
    runtime: {
      connect: vi.fn(),
      sendMessage: vi.fn(),
      onMessage: new FakeEvent<
        [{ type: string; [key: string]: unknown }, MessageSender, Mock?]
      >(),
      onConnect: new FakeEvent<[PortMock]>(),
      lastError: undefined,
    },
    debugger: {
      attach: vi.fn(),
      detach: vi.fn(),
      sendCommand: vi.fn(),
    },
  };

  (globalThis as unknown as { chrome: ChromeMock }).chrome = mock;
  return mock;
}

export function uninstallChromeMock(): void {
  delete (globalThis as unknown as { chrome?: ChromeMock }).chrome;
}

/** Encodes a string as the ArrayBuffer shape chrome puts in requestBody.raw. */
export function toRawBytes(text: string): ArrayBuffer {
  const encoded = new TextEncoder().encode(text);
  return encoded.buffer.slice(
    encoded.byteOffset,
    encoded.byteOffset + encoded.byteLength,
  ) as ArrayBuffer;
}
