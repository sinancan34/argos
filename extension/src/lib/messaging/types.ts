import type { Step, Validation } from "@/lib/schemas/scenario";
import type { StepResult, ValidationResult } from "@/lib/executor/types";
import type { DeviceMeta } from "@/lib/schemas/device";

export const EXECUTION_PORT_NAME = "argos-execution";

// --- DevTools Panel → Background (via port) ---

export interface ExecuteStepsMessage {
  type: "EXECUTE_STEPS";
  steps: Step[];
  stepTimeout: number;
  // Free-form device meta to emulate on the execution tab. Absent → no emulation.
  deviceMeta?: DeviceMeta;
}

export interface ExecuteScenarioMessage {
  type: "EXECUTE_SCENARIO";
  steps: Step[];
  validations: Validation[];
  stepTimeout: number;
  validationTimeout: number;
  // Free-form device meta to emulate on the execution tab. Absent → no emulation.
  deviceMeta?: DeviceMeta;
}

export type PanelMessage = ExecuteStepsMessage | ExecuteScenarioMessage;

// --- Background → DevTools Panel (via port) ---

export interface StepStartMessage {
  type: "STEP_START";
  stepId: string;
  stepIndex: number;
}

export interface StepSuccessMessage {
  type: "STEP_SUCCESS";
  stepId: string;
  stepIndex: number;
  duration: number;
}

export interface StepErrorMessage {
  type: "STEP_ERROR";
  stepId: string;
  stepIndex: number;
  error: string;
  duration: number;
}

export interface ExecutionCompleteMessage {
  type: "EXECUTION_COMPLETE";
  mode: "step-test" | "scenario-run";
  success: boolean;
  stepResults: StepResult[];
  validationResults?: ValidationResult[];
}

export interface ValidationPhaseStartMessage {
  type: "VALIDATION_PHASE_START";
  totalValidations: number;
  waitingMs: number;
}

export interface ValidationWaitCompleteMessage {
  type: "VALIDATION_WAIT_COMPLETE";
  capturedRequestCount: number;
}

export interface ValidationResultMessage {
  type: "VALIDATION_RESULT";
  validationId: string;
  validationIndex: number;
  result: ValidationResult;
}

export interface EmulationStatusMessage {
  type: "EMULATION_STATUS";
  // true → the device was emulated on the tab; false → emulation was skipped
  // (device had no viewport) or the debugger attach failed and the run continues
  // at the default viewport.
  applied: boolean;
}

export type BackgroundMessage =
  | StepStartMessage
  | StepSuccessMessage
  | StepErrorMessage
  | ExecutionCompleteMessage
  | ValidationPhaseStartMessage
  | ValidationWaitCompleteMessage
  | ValidationResultMessage
  | EmulationStatusMessage;

// --- Background → Content Script (one-shot) ---

export interface ExecClickMessage {
  type: "EXEC_CLICK";
  selector: string;
  timeout: number;
}

// --- Content Script → Background (response) ---

export interface ContentResponse {
  success: boolean;
  error?: string;
}
