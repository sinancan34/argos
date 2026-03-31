import type { Step, Validation } from "@/lib/schemas/scenario";
import type { StepResult, ValidationResult } from "@/lib/executor/types";

export const EXECUTION_PORT_NAME = "argos-execution";

// --- Side Panel → Background (via port) ---

export interface ExecuteStepsMessage {
  type: "EXECUTE_STEPS";
  steps: Step[];
  stepTimeout: number;
}

export interface ExecuteScenarioMessage {
  type: "EXECUTE_SCENARIO";
  steps: Step[];
  validations: Validation[];
  stepTimeout: number;
  validationTimeout: number;
}

export type SidePanelMessage = ExecuteStepsMessage | ExecuteScenarioMessage;

// --- Background → Side Panel (via port) ---

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

export type BackgroundMessage =
  | StepStartMessage
  | StepSuccessMessage
  | StepErrorMessage
  | ExecutionCompleteMessage
  | ValidationPhaseStartMessage
  | ValidationWaitCompleteMessage
  | ValidationResultMessage;

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
