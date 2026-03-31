import type { Validation } from "@/lib/schemas/scenario";
import type { ValidationResult, ParamCheckResult } from "@/lib/executor/types";
import {
  checkUrlMatch,
  parseQueryParams,
  checkParamMatch,
} from "@/lib/executor/matchers";
import { PROVIDERS } from "@/lib/validation-registry";

function getMatchingUrls(
  validation: Validation,
  capturedUrls: string[],
): string[] {
  const provider = validation.provider ?? "custom";

  if (provider === "custom") {
    if (!validation.url) return [];
    return capturedUrls.filter((url) => checkUrlMatch(validation.url!, url));
  }

  const providerDef = PROVIDERS[provider];
  if (!providerDef) return [];

  return capturedUrls.filter((url) =>
    providerDef.urlPatterns.some(
      (pattern) => new RegExp(pattern).test(url),
    ),
  );
}

function failResult(validation: Validation, urlCheckPassed: boolean): ValidationResult {
  return {
    validationId: validation.id,
    status: "fail",
    urlCheckPassed,
    paramResults: validation.params.map((p) => ({
      key: p.key,
      match: p.match,
      expected: p.value,
      actual: undefined,
      passed: false,
    })),
  };
}

export function evaluateValidation(
  validation: Validation,
  capturedUrls: string[],
): ValidationResult {
  const matchingUrls = getMatchingUrls(validation, capturedUrls);

  if (matchingUrls.length === 0) {
    return failResult(validation, false);
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

  return failResult(validation, true);
}

