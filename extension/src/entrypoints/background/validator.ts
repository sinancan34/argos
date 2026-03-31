import type { Validation } from "@/lib/schemas/scenario";
import type { ValidationResult, ParamCheckResult } from "@/lib/executor/types";
import {
  checkUrlMatch,
  parseQueryParams,
  checkParamMatch,
} from "@/lib/executor/matchers";

export function evaluateValidation(
  validation: Validation,
  capturedUrls: string[],
): ValidationResult {
  const matchedUrl = capturedUrls.find((url) =>
    checkUrlMatch(validation.url, url),
  );

  if (!matchedUrl) {
    return {
      validationId: validation.id,
      status: "fail",
      urlCheckPassed: false,
      paramResults: validation.params.map((p) => ({
        key: p.key,
        match: p.match,
        expected: p.value,
        actual: undefined,
        passed: false,
      })),
    };
  }

  const params = parseQueryParams(matchedUrl);
  const paramResults: ParamCheckResult[] = validation.params.map((pc) =>
    checkParamMatch(pc, params),
  );

  const allParamsPassed = paramResults.every((r) => r.passed);

  return {
    validationId: validation.id,
    status: allParamsPassed ? "pass" : "fail",
    matchedRequestUrl: matchedUrl,
    urlCheckPassed: true,
    paramResults,
  };
}

