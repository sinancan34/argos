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
  const matchingUrls = capturedUrls.filter((url) =>
    checkUrlMatch(validation.url, url),
  );

  if (matchingUrls.length === 0) {
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

  for (const url of matchingUrls) {
    const params = parseQueryParams(url);
    const paramResults: ParamCheckResult[] = validation.params.map((pc) =>
      checkParamMatch(pc, params),
    );

    if (paramResults.every((r) => r.passed)) {
      return {
        validationId: validation.id,
        status: "pass",
        matchedRequestUrl: url,
        urlCheckPassed: true,
        paramResults,
      };
    }
  }

  return {
    validationId: validation.id,
    status: "fail",
    urlCheckPassed: true,
    paramResults: validation.params.map((p) => ({
      key: p.key,
      match: p.match,
      expected: p.value,
      actual: undefined,
      passed: false,
    })),
  };
}

