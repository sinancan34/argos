export interface StepResult {
  stepId: string;
  command: string;
  status: "success" | "error";
  duration: number;
  error?: string;
}

export interface StepTestResult {
  mode: "step-test";
  success: boolean;
  stepResults: StepResult[];
}

export interface ScenarioRunResult {
  mode: "scenario-run";
  success: boolean;
  stepResults: StepResult[];
}

export type ExecutionResult = StepTestResult | ScenarioRunResult;
