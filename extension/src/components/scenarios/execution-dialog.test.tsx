// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ScenarioResponse } from "../../lib/schemas/scenario";
import type { BackgroundMessage } from "../../lib/messaging/types";
import type { ValidationResult } from "../../lib/executor/types";

const {
  getScenarioMock,
  getDeviceMock,
  connectExecutionPortMock,
  sendMock,
  disconnectMock,
  handlers,
} = vi.hoisted(() => ({
  getScenarioMock: vi.fn(),
  getDeviceMock: vi.fn(),
  connectExecutionPortMock: vi.fn(),
  sendMock: vi.fn(),
  disconnectMock: vi.fn(),
  handlers: {
    onMessage: null as ((message: unknown) => void) | null,
    onDisconnect: null as (() => void) | null,
  },
}));

vi.mock("../../lib/api/scenarios", () => ({
  getScenario: (id: string) => getScenarioMock(id),
}));

vi.mock("../../lib/api/devices", () => ({
  getDevice: (id: string) => getDeviceMock(id),
}));

vi.mock("../../lib/messaging/protocol", () => ({
  connectExecutionPort: (
    onMessage: (message: unknown) => void,
    onDisconnect?: () => void,
  ) => {
    handlers.onMessage = onMessage;
    handlers.onDisconnect = onDisconnect ?? null;
    connectExecutionPortMock(onMessage, onDisconnect);
    return { send: sendMock, disconnect: disconnectMock };
  },
}));

import { ExecutionDialog } from "./execution-dialog";

const SCENARIO_ID = "scenario-1";
const DEVICE_ID = "device-1";
const STEP_TIMEOUT = 5000;
const VALIDATION_TIMEOUT = 10000;

const STEPS = [
  { id: "step-1", command: "goto", params: { url: "https://example.com" } },
  { id: "step-2", command: "click", params: { selector: "#buy" } },
];

const VALIDATIONS = [
  { id: "validation-1", provider: "google_analytics", params: [] },
];

const SCENARIO: ScenarioResponse = {
  id: SCENARIO_ID,
  name: "Checkout flow",
  description: null,
  status: true,
  device_id: DEVICE_ID,
  step_timeout: STEP_TIMEOUT,
  validation_timeout: VALIDATION_TIMEOUT,
  steps: STEPS,
  validations: VALIDATIONS,
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
} as unknown as ScenarioResponse;

const DEVICE = {
  id: DEVICE_ID,
  name: "iPhone SE",
  status: true,
  meta: {
    type: "phone",
    viewport: { width: 375, height: 667, device_pixel_ratio: 2 },
  },
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
};

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

/** Renders the dialog and waits until it has connected to the background. */
async function renderRunning(scenario: ScenarioResponse | null = SCENARIO) {
  const onOpenChange = vi.fn();
  const view = render(
    <ExecutionDialog open scenario={scenario} onOpenChange={onOpenChange} />,
  );
  if (scenario) {
    await waitFor(() => expect(connectExecutionPortMock).toHaveBeenCalled());
  }
  return { ...view, onOpenChange };
}

/** Delivers a background message to the dialog. */
function deliver(message: BackgroundMessage): void {
  act(() => handlers.onMessage?.(message));
}

/** The EXECUTE_SCENARIO payload the dialog sent. */
function sentPayload(): Record<string, unknown> {
  const call = sendMock.mock.calls.at(-1);
  if (!call) throw new Error("send was not called");
  return call[0] as Record<string, unknown>;
}

describe("ExecutionDialog", () => {
  beforeEach(() => {
    getScenarioMock.mockReset();
    getDeviceMock.mockReset();
    connectExecutionPortMock.mockReset();
    sendMock.mockReset();
    disconnectMock.mockReset();
    handlers.onMessage = null;
    handlers.onDisconnect = null;

    getScenarioMock.mockResolvedValue({ data: SCENARIO });
    getDeviceMock.mockResolvedValue({ data: DEVICE });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("startup", () => {
    it("renders nothing while closed", () => {
      // Arrange & Act
      render(
        <ExecutionDialog
          open={false}
          scenario={SCENARIO}
          onOpenChange={vi.fn()}
        />,
      );

      // Assert
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    it("does not fetch while closed", () => {
      // Arrange & Act
      render(
        <ExecutionDialog
          open={false}
          scenario={SCENARIO}
          onOpenChange={vi.fn()}
        />,
      );

      // Assert
      expect(getScenarioMock).not.toHaveBeenCalled();
    });

    it("does not fetch without a scenario", () => {
      // Arrange & Act
      render(<ExecutionDialog open scenario={null} onOpenChange={vi.fn()} />);

      // Assert
      expect(getScenarioMock).not.toHaveBeenCalled();
    });

    it("reloads the scenario to get its current steps", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(getScenarioMock).toHaveBeenCalledWith(SCENARIO_ID);
    });

    it("names the scenario in the dialog", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(screen.getByText("Checkout flow")).toBeInTheDocument();
    });

    it("titles the dialog as executing", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(screen.getByText("Executing")).toBeInTheDocument();
    });

    it("lists each step as pending", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(screen.getByText("1. goto")).toBeInTheDocument();
    });

    it("numbers the steps", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(screen.getByText("2. click")).toBeInTheDocument();
    });

    it("sends the run request with the reloaded steps", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(sentPayload()).toMatchObject({
        type: "EXECUTE_SCENARIO",
        steps: STEPS,
        validations: VALIDATIONS,
        stepTimeout: STEP_TIMEOUT,
        validationTimeout: VALIDATION_TIMEOUT,
      });
    });

    it("includes the resolved device meta for emulation", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(sentPayload().deviceMeta).toEqual(DEVICE.meta);
    });

    it("shows the device name and viewport summary", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(screen.getByText("iPhone SE · 375×667 · phone")).toBeInTheDocument();
    });

    it("runs without emulation when the device cannot be loaded", async () => {
      // Arrange
      getDeviceMock.mockRejectedValue(new Error("Not found"));

      // Act
      await renderRunning();

      // Assert
      expect(sentPayload().deviceMeta).toBeUndefined();
    });

    it("still runs the steps when the device is unavailable", async () => {
      // Arrange
      getDeviceMock.mockRejectedValue(new Error("Not found"));

      // Act
      await renderRunning();

      // Assert
      expect(sendMock).toHaveBeenCalledTimes(1);
    });

    it("reports a scenario with no steps as an error", async () => {
      // Arrange
      getScenarioMock.mockResolvedValue({
        data: { ...SCENARIO, steps: [] },
      });

      // Act
      render(
        <ExecutionDialog open scenario={SCENARIO} onOpenChange={vi.fn()} />,
      );

      // Assert
      await waitFor(() =>
        expect(
          screen.getByText("No steps to execute in this scenario."),
        ).toBeInTheDocument(),
      );
    });

    it("does not connect when there are no steps", async () => {
      // Arrange
      getScenarioMock.mockResolvedValue({
        data: { ...SCENARIO, steps: [] },
      });

      // Act
      render(
        <ExecutionDialog open scenario={SCENARIO} onOpenChange={vi.fn()} />,
      );
      await waitFor(() =>
        expect(screen.getByText(/No steps to execute/)).toBeInTheDocument(),
      );

      // Assert
      expect(connectExecutionPortMock).not.toHaveBeenCalled();
    });

    it("surfaces a scenario load failure", async () => {
      // Arrange
      getScenarioMock.mockRejectedValue(new Error("Network error"));

      // Act
      render(
        <ExecutionDialog open scenario={SCENARIO} onOpenChange={vi.fn()} />,
      );

      // Assert
      await waitFor(() =>
        expect(screen.getByText("Network error")).toBeInTheDocument(),
      );
    });

    it("falls back to a generic message for a non-Error failure", async () => {
      // Arrange
      getScenarioMock.mockRejectedValue("boom");

      // Act
      render(
        <ExecutionDialog open scenario={SCENARIO} onOpenChange={vi.fn()} />,
      );

      // Assert
      await waitFor(() =>
        expect(
          screen.getByText("Failed to load scenario."),
        ).toBeInTheDocument(),
      );
    });
  });

  describe("step progress", () => {
    it("shows a step's duration on success", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "STEP_SUCCESS",
        stepId: "step-1",
        stepIndex: 0,
        duration: 1500,
      });

      // Assert
      expect(screen.getByText("(1.5s)")).toBeInTheDocument();
    });

    it("shows a step's error message", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "STEP_ERROR",
        stepId: "step-2",
        stepIndex: 1,
        error: "Element is obstructed",
        duration: 5000,
      });

      // Assert
      expect(screen.getByText("Element is obstructed")).toBeInTheDocument();
    });

    it("updates only the step the message names", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "STEP_SUCCESS",
        stepId: "step-1",
        stepIndex: 0,
        duration: 1000,
      });

      // Assert
      expect(screen.getAllByText(/\(\d\.\ds\)/)).toHaveLength(1);
    });

    it("reports emulation trouble beside the device", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({ type: "EMULATION_STATUS", status: "failed" });

      // Assert
      expect(screen.getByText("· emulation unavailable")).toBeInTheDocument();
    });

    it("stays quiet when emulation was applied", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({ type: "EMULATION_STATUS", status: "applied" });

      // Assert
      expect(
        screen.queryByText("· emulation unavailable"),
      ).not.toBeInTheDocument();
    });

    it("stays quiet when emulation was intentionally skipped", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({ type: "EMULATION_STATUS", status: "skipped" });

      // Assert
      expect(
        screen.queryByText("· emulation unavailable"),
      ).not.toBeInTheDocument();
    });
  });

  describe("validation phase", () => {
    it("switches the title while validating", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "VALIDATION_PHASE_START",
        totalValidations: 1,
        waitingMs: VALIDATION_TIMEOUT,
      });

      // Assert
      expect(screen.getByText("Validating")).toBeInTheDocument();
    });

    it("explains that it is waiting for network requests", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "VALIDATION_PHASE_START",
        totalValidations: 1,
        waitingMs: VALIDATION_TIMEOUT,
      });

      // Assert
      expect(
        screen.getByText("Waiting for network requests..."),
      ).toBeInTheDocument();
    });

    it("stops showing the wait once it completes", async () => {
      // Arrange
      await renderRunning();
      deliver({
        type: "VALIDATION_PHASE_START",
        totalValidations: 1,
        waitingMs: VALIDATION_TIMEOUT,
      });

      // Act
      deliver({ type: "VALIDATION_WAIT_COMPLETE", capturedRequestCount: 3 });

      // Assert
      expect(
        screen.queryByText("Waiting for network requests..."),
      ).not.toBeInTheDocument();
    });

    it("lists the validations once the wait completes", async () => {
      // Arrange
      await renderRunning();
      deliver({
        type: "VALIDATION_PHASE_START",
        totalValidations: 1,
        waitingMs: VALIDATION_TIMEOUT,
      });

      // Act
      deliver({ type: "VALIDATION_WAIT_COMPLETE", capturedRequestCount: 3 });

      // Assert
      expect(screen.getByText("Validation 1")).toBeInTheDocument();
    });

    it("explains a validation that matched no request", async () => {
      // Arrange
      await renderRunning();
      deliver({
        type: "VALIDATION_PHASE_START",
        totalValidations: 1,
        waitingMs: VALIDATION_TIMEOUT,
      });
      deliver({ type: "VALIDATION_WAIT_COMPLETE", capturedRequestCount: 0 });

      // Act
      deliver({
        type: "VALIDATION_RESULT",
        validationId: "validation-1",
        validationIndex: 0,
        result: makeValidationResult({
          status: "fail",
          urlCheckPassed: false,
        }),
      });

      // Assert
      expect(screen.getByText("No matching request found")).toBeInTheDocument();
    });
  });

  describe("completion", () => {
    it("titles a successful run as completed", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: true,
        stepResults: [],
        validationResults: [makeValidationResult()],
      });

      // Assert
      expect(screen.getByText("Completed")).toBeInTheDocument();
    });

    it("titles an unsuccessful run as failed", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: false,
        stepResults: [],
        validationResults: [makeValidationResult({ status: "fail" })],
      });

      // Assert
      expect(screen.getByText("Failed")).toBeInTheDocument();
    });

    it("summarizes passing steps and validations", async () => {
      // Arrange
      await renderRunning();
      deliver({
        type: "STEP_SUCCESS",
        stepId: "step-1",
        stepIndex: 0,
        duration: 100,
      });

      // Act
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: true,
        stepResults: [],
        validationResults: [makeValidationResult()],
      });

      // Assert
      expect(
        screen.getByText("2 steps passed, 1/1 validations passed."),
      ).toBeInTheDocument();
    });

    it("counts failed steps in the summary", async () => {
      // Arrange
      await renderRunning();
      deliver({
        type: "STEP_ERROR",
        stepId: "step-1",
        stepIndex: 0,
        error: "boom",
        duration: 100,
      });

      // Act
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: false,
        stepResults: [],
        validationResults: [makeValidationResult({ status: "fail" })],
      });

      // Assert
      expect(
        screen.getByText("1 step failed, 0/1 validations passed."),
      ).toBeInTheDocument();
    });

    it("replaces the streamed validation states with the final results", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: false,
        stepResults: [],
        validationResults: [
          makeValidationResult({ validationId: "v1" }),
          makeValidationResult({ validationId: "v2", status: "fail" }),
        ],
      });

      // Assert
      expect(screen.getByText("Validation 2")).toBeInTheDocument();
    });

    it("offers a close action once finished", async () => {
      // Arrange
      await renderRunning();

      // Act
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: true,
        stepResults: [],
      });

      // Assert
      expect(screen.getByRole("button", { name: "Close" })).toBeInTheDocument();
    });

    it("closes the dialog when the close action is used", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onOpenChange } = await renderRunning();
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: true,
        stepResults: [],
      });

      // Act
      await user.click(screen.getByRole("button", { name: "Close" }));

      // Assert
      expect(onOpenChange).toHaveBeenCalledWith(false);
    });
  });

  describe("cancellation", () => {
    it("offers a cancel action while running", async () => {
      // Arrange & Act
      await renderRunning();

      // Assert
      expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
    });

    it("disconnects the port when cancelled", async () => {
      // Arrange
      const user = userEvent.setup();
      await renderRunning();

      // Act
      await user.click(screen.getByRole("button", { name: "Cancel" }));

      // Assert
      expect(disconnectMock).toHaveBeenCalled();
    });

    it("closes the dialog when cancelled", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onOpenChange } = await renderRunning();

      // Act
      await user.click(screen.getByRole("button", { name: "Cancel" }));

      // Assert
      expect(onOpenChange).toHaveBeenCalledWith(false);
    });

    it("marks the run as failed when the connection drops", async () => {
      // Arrange
      await renderRunning();

      // Act
      act(() => handlers.onDisconnect?.());

      // Assert
      expect(screen.getByText("Failed")).toBeInTheDocument();
    });

    // The handler sets an errorMessage of "Connection lost.", but the block that
    // renders errorMessage is gated on `stepStates.length === 0`, and the steps are
    // always populated before the port is opened. So the reason is unreachable in
    // practice and the user only sees the "Failed" title.
    it("does not surface the reason for the dropped connection", async () => {
      // Arrange
      await renderRunning();

      // Act
      act(() => handlers.onDisconnect?.());

      // Assert
      expect(screen.queryByText("Connection lost.")).not.toBeInTheDocument();
    });

    it("ignores a disconnect after the run completed", async () => {
      // Arrange
      await renderRunning();
      deliver({
        type: "EXECUTION_COMPLETE",
        mode: "scenario-run",
        success: true,
        stepResults: [],
      });

      // Act
      act(() => handlers.onDisconnect?.());

      // Assert
      expect(screen.getByText("Completed")).toBeInTheDocument();
    });

    it("disconnects the port on unmount", async () => {
      // Arrange
      const { unmount } = await renderRunning();

      // Act
      unmount();

      // Assert
      expect(disconnectMock).toHaveBeenCalled();
    });
  });
});
