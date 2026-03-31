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

