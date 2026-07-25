export interface CapturedRequest {
  url: string;
  method?: string;
  body?: string;
  /**
   * Chrome reported a request body but could not hand over its bytes. Separates
   * "the payload was out of reach" from "this request simply had no body".
   */
  bodyUnavailable?: boolean;
}

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

