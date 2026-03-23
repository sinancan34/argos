export interface StepResult {
  stepId: string;
  command: string;
  status: "success" | "error";
  duration: number;
  error?: string;
}

export interface ParamCheckResult {
  key: string;
  match: string;
  expected?: string;
  actual?: string;
  passed: boolean;
}

export interface ValidationResult {
  validationId: string;
  status: "pass" | "fail";
  matchedRequestUrl?: string;
  urlCheckPassed: boolean;
  paramResults: ParamCheckResult[];
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
  validationResults?: ValidationResult[];
}

export type ExecutionResult = StepTestResult | ScenarioRunResult;
