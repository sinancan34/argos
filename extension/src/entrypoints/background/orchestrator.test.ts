import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  installChromeMock,
  uninstallChromeMock,
  createPortMock,
  type ChromeMock,
  type PortMock,
} from "@/test/chrome-mock";
import type { Step, Validation } from "@/lib/schemas/scenario";
import type { DeviceMeta } from "@/lib/schemas/device";
import type { ValidationResult, CapturedRequest } from "@/lib/executor/types";

const {
  applyDeviceEmulationMock,
  detachDeviceEmulationMock,
  createNetworkCaptureMock,
  evaluateValidationMock,
  captureStartMock,
  captureStopMock,
  captureWaitMock,
  callOrder,
} = vi.hoisted(() => ({
  applyDeviceEmulationMock: vi.fn(),
  detachDeviceEmulationMock: vi.fn(),
  createNetworkCaptureMock: vi.fn(),
  evaluateValidationMock: vi.fn(),
  captureStartMock: vi.fn(),
  captureStopMock: vi.fn(),
  captureWaitMock: vi.fn(),
  callOrder: [] as string[],
}));

vi.mock("./device-emulation", () => ({
  applyDeviceEmulation: (tabId: number, params: unknown) =>
    applyDeviceEmulationMock(tabId, params),
  detachDeviceEmulation: (tabId: number) => detachDeviceEmulationMock(tabId),
}));

vi.mock("./network-capture", () => ({
  createNetworkCapture: (tabId: number) => createNetworkCaptureMock(tabId),
}));

vi.mock("./validator", () => ({
  evaluateValidation: (validation: unknown, requests: unknown) =>
    evaluateValidationMock(validation, requests),
}));

import { executeSteps } from "./orchestrator";

const TAB_ID = 42;
const STEP_TIMEOUT = 5000;
const VALIDATION_TIMEOUT = 10000;
const DEFAULT_VALIDATION_WAIT = 5000;
const TARGET_URL = "https://example.com";
const SELECTOR = "#buy-button";

const GOTO_STEP: Step = {
  id: "step-1",
  command: "goto",
  params: { url: TARGET_URL },
};

const CLICK_STEP: Step = {
  id: "step-2",
  command: "click",
  params: { selector: SELECTOR },
};

const PHONE_META: DeviceMeta = {
  type: "phone",
  user_agent: "iPhone UA",
  viewport: { width: 375, height: 667, device_pixel_ratio: 2 },
  capabilities: { touch: true, mobile: true },
};

const DESKTOP_META: DeviceMeta = { type: "desktop", user_agent: "Desktop UA" };

let chromeMock: ChromeMock;
let port: PortMock;

interface PortMessage {
  type: string;
  [key: string]: unknown;
}

function makeValidation(overrides: Partial<Validation> = {}): Validation {
  return {
    id: "validation-1",
    provider: "google_analytics",
    params: [{ key: "en", match: "exact", value: "page_view" }],
    ...overrides,
  } as Validation;
}

function makeValidationResult(
  overrides: Partial<ValidationResult> = {},
): ValidationResult {
  return {
    validationId: "validation-1",
    status: "pass",
    urlCheckPassed: true,
    paramResults: [],
    ...overrides,
  };
}

/** Every message posted to the panel port, in order. */
function messages(): PortMessage[] {
  return port.postMessage.mock.calls.map((call) => call[0] as PortMessage);
}

function messageTypes(): string[] {
  return messages().map((message) => message.type);
}

function messagesOfType(type: string): PortMessage[] {
  return messages().filter((message) => message.type === type);
}

function firstOfType(type: string): PortMessage | undefined {
  return messagesOfType(type)[0];
}

/**
 * Makes goto succeed: tabs.update fires the DOMContentLoaded the orchestrator
 * waits for, and executeScript fires the CONTENT_READY the content script sends.
 */
function primeGotoSuccess(): void {
  chromeMock.tabs.update.mockImplementation(async () => {
    chromeMock.webNavigation.onDOMContentLoaded.emit({
      tabId: TAB_ID,
      frameId: 0,
    });
  });
  chromeMock.scripting.executeScript.mockImplementation(async () => {
    chromeMock.runtime.onMessage.emit(
      { type: "CONTENT_READY" },
      { tab: { id: TAB_ID } },
    );
    return [];
  });
}

function primeCapture(requests: CapturedRequest[] = []): void {
  captureWaitMock.mockResolvedValue(requests);
  createNetworkCaptureMock.mockReturnValue({
    start: captureStartMock,
    stop: captureStopMock,
    waitAndCollect: captureWaitMock,
  });
}

describe("executeSteps", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    chromeMock = installChromeMock();
    port = createPortMock();

    callOrder.length = 0;

    chromeMock.tabs.create.mockResolvedValue({ id: TAB_ID });
    chromeMock.tabs.remove.mockImplementation(async () => {
      callOrder.push("tabs.remove");
    });
    chromeMock.tabs.sendMessage.mockResolvedValue({ success: true });

    applyDeviceEmulationMock.mockReset();
    applyDeviceEmulationMock.mockResolvedValue(true);
    detachDeviceEmulationMock.mockReset();
    detachDeviceEmulationMock.mockImplementation(async () => {
      callOrder.push("detachDeviceEmulation");
    });
    createNetworkCaptureMock.mockReset();
    evaluateValidationMock.mockReset();
    evaluateValidationMock.mockReturnValue(makeValidationResult());
    captureStartMock.mockReset();
    captureStopMock.mockReset();
    captureWaitMock.mockReset();

    primeGotoSuccess();
    primeCapture();
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe("execution tab lifecycle", () => {
    it("creates an active about:blank tab", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.create).toHaveBeenCalledWith({
        url: "about:blank",
        active: true,
      });
    });

    it("throws when the created tab has no id", async () => {
      // Arrange
      chromeMock.tabs.create.mockResolvedValue({});

      // Act & Assert
      await expect(
        executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test"),
      ).rejects.toThrow("Failed to create execution tab");
    });

    it("removes the tab after a successful run", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.remove).toHaveBeenCalledWith(TAB_ID);
    });

    it("removes the tab after a failed step", async () => {
      // Arrange
      chromeMock.tabs.sendMessage.mockResolvedValue({
        success: false,
        error: "not found",
      });

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.remove).toHaveBeenCalledWith(TAB_ID);
    });

    it("swallows a failure to remove the tab", async () => {
      // Arrange
      chromeMock.tabs.remove.mockRejectedValue(new Error("No such tab"));

      // Act & Assert
      await expect(
        executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test"),
      ).resolves.toBeUndefined();
    });

    it("does not remove a tab the user already closed", async () => {
      // Arrange — no navigation event, so the step is still in flight
      chromeMock.tabs.update.mockResolvedValue(undefined);
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(0);

      // Act
      chromeMock.tabs.onRemoved.emit(TAB_ID, {
        windowId: 1,
        isWindowClosing: false,
      });
      await run;

      // Assert
      expect(chromeMock.tabs.remove).not.toHaveBeenCalled();
    });

    it("ignores the removal of an unrelated tab", async () => {
      // Arrange
      const otherTabId = TAB_ID + 1;

      // Act
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      chromeMock.tabs.onRemoved.emit(otherTabId, {
        windowId: 1,
        isWindowClosing: false,
      });
      await run;

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.success).toBe(true);
    });

    it("removes the tab-removed listener when the run ends", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.onRemoved.listenerCount).toBe(0);
    });

    it("removes the port disconnect listener when the run ends", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(port.onDisconnect.listenerCount).toBe(0);
    });
  });

  describe("goto command", () => {
    it("navigates the execution tab to the step url", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.update).toHaveBeenCalledWith(TAB_ID, {
        url: TARGET_URL,
      });
    });

    it("injects the content script after navigating", async () => {
      // Arrange — the literal path is what WXT emits for entrypoints/content

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.scripting.executeScript).toHaveBeenCalledWith({
        target: { tabId: TAB_ID },
        files: ["content-scripts/content.js"],
      });
    });

    it("fails the step when the url param is missing", async () => {
      // Arrange
      const step: Step = { id: "step-1", command: "goto", params: {} };

      // Act
      await executeSteps(port, [step], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        "goto step missing 'url' param",
      );
    });

    it("fails the step when the url param is an empty string", async () => {
      // Arrange
      const step: Step = { id: "step-1", command: "goto", params: { url: "" } };

      // Act
      await executeSteps(port, [step], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        "goto step missing 'url' param",
      );
    });

    it("fails the step when navigation reports an error", async () => {
      // Arrange
      chromeMock.tabs.update.mockImplementation(async () => {
        chromeMock.webNavigation.onErrorOccurred.emit({
          tabId: TAB_ID,
          frameId: 0,
          error: "net::ERR_NAME_NOT_RESOLVED",
        });
      });

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        "Navigation failed: net::ERR_NAME_NOT_RESOLVED",
      );
    });

    it("ignores a DOMContentLoaded from a subframe", async () => {
      // Arrange — only the top frame (frameId 0) completes the navigation
      chromeMock.tabs.update.mockImplementation(async () => {
        chromeMock.webNavigation.onDOMContentLoaded.emit({
          tabId: TAB_ID,
          frameId: 1,
        });
      });

      // Act
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(STEP_TIMEOUT);
      await run;

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        `Timeout after ${STEP_TIMEOUT}ms: goto`,
      );
    });

    it("ignores a DOMContentLoaded from a different tab", async () => {
      // Arrange
      chromeMock.tabs.update.mockImplementation(async () => {
        chromeMock.webNavigation.onDOMContentLoaded.emit({
          tabId: TAB_ID + 1,
          frameId: 0,
        });
      });

      // Act
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(STEP_TIMEOUT);
      await run;

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        `Timeout after ${STEP_TIMEOUT}ms: goto`,
      );
    });

    it("ignores a CONTENT_READY from a different tab", async () => {
      // Arrange
      chromeMock.scripting.executeScript.mockImplementation(async () => {
        chromeMock.runtime.onMessage.emit(
          { type: "CONTENT_READY" },
          { tab: { id: TAB_ID + 1 } },
        );
        return [];
      });

      // Act
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(STEP_TIMEOUT);
      await run;

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        `Timeout after ${STEP_TIMEOUT}ms: goto`,
      );
    });

    it("unregisters the navigation listeners after a successful goto", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.webNavigation.onDOMContentLoaded.listenerCount).toBe(0);
    });

    it("unregisters the content-ready listener after a successful goto", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.runtime.onMessage.listenerCount).toBe(0);
    });

    it("fails the step when script injection rejects", async () => {
      // Arrange
      chromeMock.scripting.executeScript.mockRejectedValue(
        new Error("Cannot access contents of the page"),
      );

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        "Cannot access contents of the page",
      );
    });
  });

  describe("click command", () => {
    it("sends EXEC_CLICK with the selector and timeout", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.sendMessage).toHaveBeenCalledWith(TAB_ID, {
        type: "EXEC_CLICK",
        selector: SELECTOR,
        timeout: STEP_TIMEOUT,
      });
    });

    it("succeeds when the content script reports success", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messagesOfType("STEP_SUCCESS")).toHaveLength(1);
    });

    it("fails the step with the content script's error message", async () => {
      // Arrange
      chromeMock.tabs.sendMessage.mockResolvedValue({
        success: false,
        error: "Element is obstructed",
      });

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe("Element is obstructed");
    });

    it("falls back to a generic message when the failure carries no error", async () => {
      // Arrange
      chromeMock.tabs.sendMessage.mockResolvedValue({ success: false });

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe("Click failed");
    });

    it("falls back to a generic message when the response is undefined", async () => {
      // Arrange — happens when no content script is listening
      chromeMock.tabs.sendMessage.mockResolvedValue(undefined);

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe("Click failed");
    });

    it("fails the step when the selector param is missing", async () => {
      // Arrange
      const step: Step = { id: "step-1", command: "click", params: {} };

      // Act
      await executeSteps(port, [step], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        "click step missing 'selector' param",
      );
    });

    it("fails the step when sendMessage rejects", async () => {
      // Arrange — no receiving end, e.g. the page navigated away
      chromeMock.tabs.sendMessage.mockRejectedValue(
        new Error("Could not establish connection"),
      );

      // Act
      await executeSteps(port, [CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        "Could not establish connection",
      );
    });
  });

  describe("unknown command", () => {
    it("fails the step naming the command", async () => {
      // Arrange
      const step = {
        id: "step-1",
        command: "scroll",
        params: {},
      } as unknown as Step;

      // Act
      await executeSteps(port, [step], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe("Unknown command: scroll");
    });
  });

  describe("step progress messages", () => {
    it("posts STEP_START before the command runs", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messageTypes()[0]).toBe("STEP_START");
    });

    it("posts STEP_START with the step id and index", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP, CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messagesOfType("STEP_START")[1]).toMatchObject({
        stepId: CLICK_STEP.id,
        stepIndex: 1,
      });
    });

    it("posts STEP_SUCCESS with the step id and index", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_SUCCESS")).toMatchObject({
        stepId: GOTO_STEP.id,
        stepIndex: 0,
      });
    });

    it("reports a numeric duration on success", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(typeof firstOfType("STEP_SUCCESS")?.duration).toBe("number");
    });

    it("runs steps in order", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP, CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(
        messagesOfType("STEP_START").map((message) => message.stepId),
      ).toEqual([GOTO_STEP.id, CLICK_STEP.id]);
    });

    it("posts no step messages for an empty step list", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messageTypes()).toEqual(["EXECUTION_COMPLETE"]);
    });

    it("swallows a postMessage failure on a disconnected port", async () => {
      // Arrange
      port.postMessage.mockImplementation(() => {
        throw new Error("Attempting to use a disconnected port object");
      });

      // Act & Assert
      await expect(
        executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test"),
      ).resolves.toBeUndefined();
    });
  });

  describe("step failure handling", () => {
    it("stops before the remaining steps", async () => {
      // Arrange — the first step fails
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(port, [GOTO_STEP, CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messagesOfType("STEP_START")).toHaveLength(1);
    });

    it("reports the run as unsuccessful", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.success).toBe(false);
    });

    it("includes the failed step in the results", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.stepResults).toEqual([
        expect.objectContaining({
          stepId: GOTO_STEP.id,
          command: "goto",
          status: "error",
          error: "nav boom",
        }),
      ]);
    });

    it("sends an empty validationResults array on step failure", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.validationResults).toEqual([]);
    });

    it("stringifies a non-Error thrown value", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue("plain string failure");

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe("plain string failure");
    });

    it("skips the validation phase after a step failure", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(messagesOfType("VALIDATION_PHASE_START")).toHaveLength(0);
    });

    it("stops the network capture after a step failure", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(captureStopMock).toHaveBeenCalled();
    });

    it("times out a step that never completes", async () => {
      // Arrange — no navigation event ever fires
      chromeMock.tabs.update.mockResolvedValue(undefined);

      // Act
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(STEP_TIMEOUT);
      await run;

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe(
        `Timeout after ${STEP_TIMEOUT}ms: goto`,
      );
    });

    it("does not time out just before the timeout elapses", async () => {
      // Arrange
      chromeMock.tabs.update.mockResolvedValue(undefined);

      // Act
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(STEP_TIMEOUT - 1);
      const errorsBefore = messagesOfType("STEP_ERROR").length;
      await vi.advanceTimersByTimeAsync(1);
      await run;

      // Assert
      expect(errorsBefore).toBe(0);
    });

    it("fails the step when the tab is closed mid-step", async () => {
      // Arrange
      chromeMock.tabs.update.mockResolvedValue(undefined);
      const run = executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");
      await vi.advanceTimersByTimeAsync(0);

      // Act
      chromeMock.tabs.onRemoved.emit(TAB_ID, {
        windowId: 1,
        isWindowClosing: false,
      });
      await run;

      // Assert
      expect(firstOfType("STEP_ERROR")?.error).toBe("Execution tab was closed");
    });
  });

  describe("device emulation", () => {
    it("applies emulation before the first navigation", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(applyDeviceEmulationMock).toHaveBeenCalledWith(
        TAB_ID,
        expect.objectContaining({
          deviceMetrics: expect.objectContaining({ width: 375, height: 667 }),
        }),
      );
    });

    it("reports applied when emulation succeeds", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(firstOfType("EMULATION_STATUS")?.status).toBe("applied");
    });

    it("reports failed when emulation could not be applied", async () => {
      // Arrange
      applyDeviceEmulationMock.mockResolvedValue(false);

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(firstOfType("EMULATION_STATUS")?.status).toBe("failed");
    });

    it("continues the run when emulation fails", async () => {
      // Arrange
      applyDeviceEmulationMock.mockResolvedValue(false);

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.success).toBe(true);
    });

    it("reports skipped for a device with no viewport", async () => {
      // Arrange — a Desktop device intentionally carries no viewport

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        DESKTOP_META,
      );

      // Assert
      expect(firstOfType("EMULATION_STATUS")?.status).toBe("skipped");
    });

    it("does not attach the debugger for a device with no viewport", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        DESKTOP_META,
      );

      // Assert
      expect(applyDeviceEmulationMock).not.toHaveBeenCalled();
    });

    it("posts no emulation status when no device meta is supplied", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messagesOfType("EMULATION_STATUS")).toHaveLength(0);
    });

    it("posts the emulation status before the first step starts", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(messageTypes()[0]).toBe("EMULATION_STATUS");
    });

    it("detaches the debugger when emulation was applied", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(detachDeviceEmulationMock).toHaveBeenCalledWith(TAB_ID);
    });

    it("does not detach when emulation was never applied", async () => {
      // Arrange
      applyDeviceEmulationMock.mockResolvedValue(false);

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(detachDeviceEmulationMock).not.toHaveBeenCalled();
    });

    it("removes the tab before detaching the debugger", async () => {
      // Arrange — detaching first would flash the page back to the default viewport

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(callOrder).toEqual(["tabs.remove", "detachDeviceEmulation"]);
    });

    it("still detaches after a step failure", async () => {
      // Arrange
      chromeMock.tabs.update.mockRejectedValue(new Error("nav boom"));

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        PHONE_META,
      );

      // Assert
      expect(detachDeviceEmulationMock).toHaveBeenCalledWith(TAB_ID);
    });
  });

  describe("network capture wiring", () => {
    it("does not capture in step-test mode", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(createNetworkCaptureMock).not.toHaveBeenCalled();
    });

    it("captures on the execution tab in scenario-run mode", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(createNetworkCaptureMock).toHaveBeenCalledWith(TAB_ID);
    });

    it("starts the capture before the first step", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(captureStartMock).toHaveBeenCalledTimes(1);
    });

    it("does not capture when the validation list is empty", async () => {
      // Arrange — nothing to validate against

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(createNetworkCaptureMock).not.toHaveBeenCalled();
    });

    it("does not capture when validations are omitted in scenario-run mode", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "scenario-run");

      // Assert
      expect(createNetworkCaptureMock).not.toHaveBeenCalled();
    });

    it("stops the capture when the run ends", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(captureStopMock).toHaveBeenCalled();
    });
  });

  describe("validation phase", () => {
    const VALIDATIONS = [
      makeValidation({ id: "validation-1" }),
      makeValidation({ id: "validation-2" }),
    ];

    it("announces the validation count and wait window", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(firstOfType("VALIDATION_PHASE_START")).toMatchObject({
        totalValidations: 2,
        waitingMs: VALIDATION_TIMEOUT,
      });
    });

    it("falls back to a default wait when no validation timeout is given", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
      );

      // Assert
      expect(firstOfType("VALIDATION_PHASE_START")?.waitingMs).toBe(
        DEFAULT_VALIDATION_WAIT,
      );
    });

    it("waits the validation timeout for late pixel fires", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(captureWaitMock).toHaveBeenCalledWith(VALIDATION_TIMEOUT);
    });

    it("reports how many requests were captured", async () => {
      // Arrange
      primeCapture([
        { url: "https://a.example.com/g/collect" },
        { url: "https://b.example.com/g/collect" },
      ]);

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(firstOfType("VALIDATION_WAIT_COMPLETE")?.capturedRequestCount).toBe(
        2,
      );
    });

    it("evaluates each validation against the captured requests", async () => {
      // Arrange
      const captured = [{ url: "https://a.example.com/g/collect" }];
      primeCapture(captured);

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(evaluateValidationMock).toHaveBeenCalledWith(
        VALIDATIONS[0],
        captured,
      );
    });

    it("evaluates every validation exactly once", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(evaluateValidationMock).toHaveBeenCalledTimes(2);
    });

    it("streams one result message per validation", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(messagesOfType("VALIDATION_RESULT")).toHaveLength(2);
    });

    it("tags each result with its validation id and index", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(messagesOfType("VALIDATION_RESULT")[1]).toMatchObject({
        validationId: "validation-2",
        validationIndex: 1,
      });
    });

    it("reports success when every validation passes", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.success).toBe(true);
    });

    it("reports failure when a single validation fails", async () => {
      // Arrange
      evaluateValidationMock
        .mockReturnValueOnce(makeValidationResult({ status: "pass" }))
        .mockReturnValueOnce(makeValidationResult({ status: "fail" }));

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.success).toBe(false);
    });

    it("includes all validation results in the completion message", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.validationResults).toHaveLength(
        2,
      );
    });

    it("emits the validation messages in order", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(messageTypes()).toEqual([
        "STEP_START",
        "STEP_SUCCESS",
        "VALIDATION_PHASE_START",
        "VALIDATION_WAIT_COMPLETE",
        "VALIDATION_RESULT",
        "EXECUTION_COMPLETE",
      ]);
    });

    it("labels the completion message with the scenario-run mode", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.mode).toBe("scenario-run");
    });
  });

  describe("step-test mode completion", () => {
    it("labels the completion message with the step-test mode", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.mode).toBe("step-test");
    });

    it("omits validationResults entirely", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")).not.toHaveProperty(
        "validationResults",
      );
    });

    it("includes a success result per step", async () => {
      // Arrange — primed in beforeEach

      // Act
      await executeSteps(port, [GOTO_STEP, CLICK_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(firstOfType("EXECUTION_COMPLETE")?.stepResults).toHaveLength(2);
    });
  });

  describe("cancellation via port disconnect", () => {
    it("stops before the next step when the port disconnects", async () => {
      // Arrange — disconnect fires while the first step is running
      chromeMock.tabs.update.mockImplementation(async () => {
        port.onDisconnect.emit();
        chromeMock.webNavigation.onDOMContentLoaded.emit({
          tabId: TAB_ID,
          frameId: 0,
        });
      });

      // Act
      await executeSteps(port, [GOTO_STEP, GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messagesOfType("STEP_START")).toHaveLength(1);
    });

    it("posts no completion message once aborted", async () => {
      // Arrange
      chromeMock.tabs.update.mockImplementation(async () => {
        port.onDisconnect.emit();
        chromeMock.webNavigation.onDOMContentLoaded.emit({
          tabId: TAB_ID,
          frameId: 0,
        });
      });

      // Act
      await executeSteps(port, [GOTO_STEP, GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(messagesOfType("EXECUTION_COMPLETE")).toHaveLength(0);
    });

    it("still removes the execution tab after an abort", async () => {
      // Arrange
      chromeMock.tabs.update.mockImplementation(async () => {
        port.onDisconnect.emit();
        chromeMock.webNavigation.onDOMContentLoaded.emit({
          tabId: TAB_ID,
          frameId: 0,
        });
      });

      // Act
      await executeSteps(port, [GOTO_STEP, GOTO_STEP], STEP_TIMEOUT, "step-test");

      // Assert
      expect(chromeMock.tabs.remove).toHaveBeenCalledWith(TAB_ID);
    });

    it("skips the validation phase once aborted", async () => {
      // Arrange
      chromeMock.tabs.update.mockImplementation(async () => {
        port.onDisconnect.emit();
        chromeMock.webNavigation.onDOMContentLoaded.emit({
          tabId: TAB_ID,
          frameId: 0,
        });
      });

      // Act
      await executeSteps(
        port,
        [GOTO_STEP],
        STEP_TIMEOUT,
        "scenario-run",
        [makeValidation()],
        VALIDATION_TIMEOUT,
      );

      // Assert
      expect(messagesOfType("VALIDATION_PHASE_START")).toHaveLength(0);
    });
  });
});
