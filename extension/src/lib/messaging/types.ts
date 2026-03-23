import type { Step } from "@/lib/schemas/scenario";
import type { SelectorEntry } from "@/lib/commands";
import type { StepResult } from "@/lib/executor/types";

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
  validations: unknown[];
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
}

export type BackgroundMessage =
  | StepStartMessage
  | StepSuccessMessage
  | StepErrorMessage
  | ExecutionCompleteMessage;

// --- Background → Content Script (one-shot) ---

export interface ExecClickMessage {
  type: "EXEC_CLICK";
  selectors: SelectorEntry[];
}

export type ContentMessage = ExecClickMessage;

// --- Content Script → Background (response) ---

export interface ContentResponse {
  success: boolean;
  error?: string;
}

// --- Content Script → Background (notification) ---

export interface ContentReadyMessage {
  type: "CONTENT_READY";
}
