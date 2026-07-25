import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  installChromeMock,
  uninstallChromeMock,
  createPortMock,
  type ChromeMock,
  type PortMock,
} from "@/test/chrome-mock";
import type { PanelMessage } from "@/lib/messaging/types";

const { executeStepsMock } = vi.hoisted(() => {
  // defineBackground is a WXT auto-import that does not exist under vitest.
  // Stubbing it to return its argument makes the module's default export the
  // registration callback, so a test can run it against the chrome fake.
  (globalThis as unknown as { defineBackground: unknown }).defineBackground = (
    main: () => void,
  ) => main;

  return { executeStepsMock: vi.fn() };
});

vi.mock("./orchestrator", () => ({
  executeSteps: (...args: unknown[]) => executeStepsMock(...args),
}));

import registerBackground from "./index";

const PICKER_TAB_ID = 7;
const STEP_TIMEOUT = 5000;
const VALIDATION_TIMEOUT = 10000;
const PICKER_SCRIPT = "/content-scripts/picker.js";

const STEPS = [
  { id: "step-1", command: "goto", params: { url: "https://example.com" } },
];
const VALIDATIONS = [
  { id: "validation-1", provider: "custom", params: [] },
];
const DEVICE_META = { type: "phone", viewport: { width: 375, height: 667 } };

const EXECUTE_STEPS_MESSAGE = {
  type: "EXECUTE_STEPS",
  steps: STEPS,
  stepTimeout: STEP_TIMEOUT,
  deviceMeta: DEVICE_META,
} as unknown as PanelMessage;

const EXECUTE_SCENARIO_MESSAGE = {
  type: "EXECUTE_SCENARIO",
  steps: STEPS,
  validations: VALIDATIONS,
  stepTimeout: STEP_TIMEOUT,
  validationTimeout: VALIDATION_TIMEOUT,
  deviceMeta: DEVICE_META,
} as unknown as PanelMessage;

let chromeMock: ChromeMock;

/** Delivers a one-shot runtime message and returns the sendResponse spy. */
function send(message: Record<string, unknown>) {
  const sendResponse = vi.fn();
  chromeMock.runtime.onMessage.emit(
    message as { type: string },
    {},
    sendResponse as never,
  );
  return sendResponse;
}

/** Connects a port and returns it, already wired to the background. */
function connect(name = "argos-execution"): PortMock {
  const port = createPortMock(name);
  chromeMock.runtime.onConnect.emit(port);
  return port;
}

/** Lets pending promise callbacks run. */
async function flush(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
}

describe("background registration", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    executeStepsMock.mockReset();
    executeStepsMock.mockResolvedValue(undefined);
    chromeMock.scripting.executeScript.mockResolvedValue([]);
    chromeMock.tabs.sendMessage.mockResolvedValue(undefined);
    registerBackground();
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.restoreAllMocks();
  });

  describe("PING", () => {
    it("answers with PONG", () => {
      // Arrange — background registered in beforeEach

      // Act
      const sendResponse = send({ type: "PING" });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({ type: "PONG" });
    });
  });

  describe("PICKER_START", () => {
    it("injects the picker script into the supplied tab", async () => {
      // Arrange — background registered in beforeEach

      // Act
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(chromeMock.scripting.executeScript).toHaveBeenCalledWith({
        target: { tabId: PICKER_TAB_ID },
        files: [PICKER_SCRIPT],
      });
    });

    it("confirms the started picker with its tab id", async () => {
      // Arrange — background registered in beforeEach

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: true,
        tabId: PICKER_TAB_ID,
      });
    });

    it("rejects a message with no tab id rather than guessing one", () => {
      // Arrange — guessing would target the wrong window when DevTools is undocked

      // Act
      const sendResponse = send({ type: "PICKER_START" });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "No target tab supplied",
      });
    });

    it("rejects a non-numeric tab id", () => {
      // Arrange — background registered in beforeEach

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: "7" });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "No target tab supplied",
      });
    });

    it("rejects a null tab id", () => {
      // Arrange — background registered in beforeEach

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: null });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "No target tab supplied",
      });
    });

    it("injects nothing when the tab id is invalid", () => {
      // Arrange — background registered in beforeEach

      // Act
      send({ type: "PICKER_START", tabId: undefined });

      // Assert
      expect(chromeMock.scripting.executeScript).not.toHaveBeenCalled();
    });

    it("accepts tab id 0", async () => {
      // Arrange — 0 is a valid tab id

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: 0 });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({ success: true, tabId: 0 });
    });

    it("refuses a second picker while one is active", async () => {
      // Arrange
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "Another operation is in progress",
      });
    });

    it("refuses a picker while an execution is running", () => {
      // Arrange — a never-settling run keeps the executing flag set
      executeStepsMock.mockReturnValue(new Promise(() => {}));
      const port = connect();
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "Another operation is in progress",
      });
    });

    it("reports an injection failure", async () => {
      // Arrange — e.g. the tab is a chrome:// page
      chromeMock.scripting.executeScript.mockRejectedValue(
        new Error("Cannot access a chrome:// URL"),
      );

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "Cannot access a chrome:// URL",
      });
    });

    it("stringifies a non-Error injection failure", async () => {
      // Arrange
      chromeMock.scripting.executeScript.mockRejectedValue("plain failure");

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: false,
        error: "plain failure",
      });
    });

    it("frees the picker slot after an injection failure", async () => {
      // Arrange
      chromeMock.scripting.executeScript.mockRejectedValueOnce(
        new Error("boom"),
      );
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: true,
        tabId: PICKER_TAB_ID,
      });
    });
  });

  describe("PICKER_CANCEL", () => {
    it("tells the active picker's tab to cancel", async () => {
      // Arrange
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Act
      send({ type: "PICKER_CANCEL" });

      // Assert
      expect(chromeMock.tabs.sendMessage).toHaveBeenCalledWith(PICKER_TAB_ID, {
        type: "PICKER_CANCEL",
      });
    });

    it("confirms the cancellation", () => {
      // Arrange — background registered in beforeEach

      // Act
      const sendResponse = send({ type: "PICKER_CANCEL" });

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({ success: true });
    });

    it("messages no tab when no picker is active", () => {
      // Arrange — background registered in beforeEach

      // Act
      send({ type: "PICKER_CANCEL" });

      // Assert
      expect(chromeMock.tabs.sendMessage).not.toHaveBeenCalled();
    });

    it("swallows a failure to reach the picker tab", async () => {
      // Arrange — the tab may already be gone
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();
      chromeMock.tabs.sendMessage.mockRejectedValue(new Error("No receiver"));

      // Act
      const sendResponse = send({ type: "PICKER_CANCEL" });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({ success: true });
    });

    it("frees the picker slot", async () => {
      // Arrange
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();
      send({ type: "PICKER_CANCEL" });

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: true,
        tabId: PICKER_TAB_ID,
      });
    });
  });

  describe("picker result relay", () => {
    it("lets a PICKER_RESULT keep propagating to the panel", () => {
      // Arrange — returning false is what leaves the message unconsumed
      const listener = vi.fn();
      chromeMock.runtime.onMessage.addListener(listener);

      // Act
      const returned = chromeMock.runtime.onMessage.emit(
        { type: "PICKER_RESULT", selectors: { primary: "#a", alternatives: [] } },
        {},
      );

      // Assert
      expect(returned).toBeUndefined();
    });

    it("frees the picker slot on a result", async () => {
      // Arrange
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();
      send({
        type: "PICKER_RESULT",
        selectors: { primary: "#a", alternatives: [] },
      });

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: true,
        tabId: PICKER_TAB_ID,
      });
    });

    it("frees the picker slot on an error", async () => {
      // Arrange
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();
      send({ type: "PICKER_ERROR", error: "Picker cancelled" });

      // Act
      const sendResponse = send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();

      // Assert
      expect(sendResponse).toHaveBeenCalledWith({
        success: true,
        tabId: PICKER_TAB_ID,
      });
    });

    it("sends no response for a relayed result", () => {
      // Arrange — the panel, not the background, consumes it

      // Act
      const sendResponse = send({
        type: "PICKER_RESULT",
        selectors: { primary: "#a", alternatives: [] },
      });

      // Assert
      expect(sendResponse).not.toHaveBeenCalled();
    });
  });

  describe("execution port", () => {
    it("ignores a port with an unrecognized name", () => {
      // Arrange & Act
      const port = connect("some-other-port");

      // Assert
      expect(port.onMessage.listenerCount).toBe(0);
    });

    it("listens on the execution port", () => {
      // Arrange & Act
      const port = connect();

      // Assert
      expect(port.onMessage.listenerCount).toBe(1);
    });

    it("runs a step test with no validations", () => {
      // Arrange
      const port = connect();

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert
      expect(executeStepsMock).toHaveBeenCalledWith(
        port,
        STEPS,
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        DEVICE_META,
      );
    });

    it("runs a scenario with its validations and wait window", () => {
      // Arrange
      const port = connect();

      // Act
      port.onMessage.emit(EXECUTE_SCENARIO_MESSAGE);

      // Assert
      expect(executeStepsMock).toHaveBeenCalledWith(
        port,
        STEPS,
        STEP_TIMEOUT,
        "scenario-run",
        VALIDATIONS,
        VALIDATION_TIMEOUT,
        DEVICE_META,
      );
    });

    it("ignores an unrecognized panel message", () => {
      // Arrange
      const port = connect();

      // Act
      port.onMessage.emit({ type: "SOMETHING_ELSE" } as unknown as PanelMessage);

      // Assert
      expect(executeStepsMock).not.toHaveBeenCalled();
    });

    it("refuses a second run while one is in flight", () => {
      // Arrange
      executeStepsMock.mockReturnValue(new Promise(() => {}));
      const port = connect();
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert
      expect(executeStepsMock).toHaveBeenCalledTimes(1);
    });

    it("refuses a run while the picker is active", async () => {
      // Arrange
      send({ type: "PICKER_START", tabId: PICKER_TAB_ID });
      await flush();
      const port = connect();

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert
      expect(executeStepsMock).not.toHaveBeenCalled();
    });

    it("accepts another run after the previous one finishes", async () => {
      // Arrange
      const port = connect();
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);
      await flush();

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert
      expect(executeStepsMock).toHaveBeenCalledTimes(2);
    });

    it("reports a failed step-test run to the panel", async () => {
      // Arrange
      executeStepsMock.mockRejectedValue(new Error("orchestrator blew up"));
      const port = connect();

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);
      await flush();

      // Assert
      expect(port.postMessage).toHaveBeenCalledWith({
        type: "EXECUTION_COMPLETE",
        mode: "step-test",
        success: false,
        stepResults: [],
      });
    });

    it("reports a failed scenario run with empty validation results", async () => {
      // Arrange
      executeStepsMock.mockRejectedValue(new Error("orchestrator blew up"));
      const port = connect();

      // Act
      port.onMessage.emit(EXECUTE_SCENARIO_MESSAGE);
      await flush();

      // Assert
      expect(port.postMessage).toHaveBeenCalledWith({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: false,
        stepResults: [],
        validationResults: [],
      });
    });

    it("swallows a post to an already disconnected port", async () => {
      // Arrange
      executeStepsMock.mockRejectedValue(new Error("orchestrator blew up"));
      const port = connect();
      port.postMessage.mockImplementation(() => {
        throw new Error("Attempting to use a disconnected port object");
      });

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert
      await expect(flush()).resolves.toBeUndefined();
    });

    it("frees the execution slot after a failed run", async () => {
      // Arrange
      executeStepsMock.mockRejectedValueOnce(new Error("boom"));
      const port = connect();
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);
      await flush();

      // Act
      port.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert
      expect(executeStepsMock).toHaveBeenCalledTimes(2);
    });

    it("supports two independent panel connections", () => {
      // Arrange — DevTools opens per tab, so each inspected tab gets its own panel
      const first = connect();
      const second = connect();

      // Act
      first.onMessage.emit(EXECUTE_STEPS_MESSAGE);
      second.onMessage.emit(EXECUTE_STEPS_MESSAGE);

      // Assert — the second is rejected silently by the executing guard
      expect(executeStepsMock).toHaveBeenCalledTimes(1);
    });

    it("passes no device meta when the panel omits it", () => {
      // Arrange
      const port = connect();

      // Act
      port.onMessage.emit({
        type: "EXECUTE_STEPS",
        steps: STEPS,
        stepTimeout: STEP_TIMEOUT,
      } as unknown as PanelMessage);

      // Assert
      expect(executeStepsMock).toHaveBeenCalledWith(
        port,
        STEPS,
        STEP_TIMEOUT,
        "step-test",
        undefined,
        undefined,
        undefined,
      );
    });
  });
});
