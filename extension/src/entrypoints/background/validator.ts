import type { Validation } from "@/lib/schemas/scenario";
import type {
  CapturedRequest,
  ValidationResult,
  ParamCheckResult,
} from "@/lib/executor/types";
import {
  checkUrlMatch,
  parseQueryParams,
  parseBodyLines,
  mergeParamMaps,
  parseGA4Items,
  checkParamMatch,
} from "@/lib/executor/matchers";
import { PROVIDERS } from "@/lib/validation-registry";

function getMatchingRequests(
  validation: Validation,
  capturedRequests: CapturedRequest[],
): CapturedRequest[] {
  const provider = validation.provider ?? "custom";

  if (provider === "custom") {
    if (!validation.url) return [];
    return capturedRequests.filter((req) =>
      checkUrlMatch(validation.url!, req.url),
    );
  }

  const providerDef = PROVIDERS[provider];
  if (!providerDef) return [];

  const constraints = providerDef.paramConstraints ?? [];

  return capturedRequests.filter((req) => {
    const urlMatches = providerDef.urlPatterns.some((pattern) =>
      new RegExp(pattern).test(req.url),
    );
    if (!urlMatches) return false;
    if (constraints.length === 0) return true;

    const urlParams = parseQueryParams(req.url);
    return constraints.every((c) => checkParamMatch(c, urlParams).passed);
  });
}

function buildParamSets(
  request: CapturedRequest,
  isGA4: boolean,
): Map<string, string[]>[] {
  const urlParams = parseQueryParams(request.url);

  if (!request.body) {
    const combined = isGA4
      ? mergeParamMaps(urlParams, parseGA4Items(urlParams))
      : urlParams;
    return [combined];
  }

  const bodyLines = parseBodyLines(request.body);

  if (bodyLines.length === 0) {
    const combined = isGA4
      ? mergeParamMaps(urlParams, parseGA4Items(urlParams))
      : urlParams;
    return [combined];
  }

  return bodyLines.map((lineParams) => {
    const merged = mergeParamMaps(urlParams, lineParams);
    if (isGA4) {
      return mergeParamMaps(merged, parseGA4Items(merged));
    }
    return merged;
  });
}

function failResult(
  validation: Validation,
  urlCheckPassed: boolean,
): ValidationResult {
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
  capturedRequests: CapturedRequest[],
): ValidationResult {
  const matchingRequests = getMatchingRequests(validation, capturedRequests);

  if (matchingRequests.length === 0) {
    return failResult(validation, false);
  }

  const provider = validation.provider ?? "custom";
  const isGA4 = provider === "google_analytics";

  for (const request of matchingRequests) {
    const paramSets = buildParamSets(request, isGA4);

    for (const params of paramSets) {
      const paramResults: ParamCheckResult[] = validation.params.map((pc) =>
        checkParamMatch(pc, params),
      );

      if (paramResults.every((r) => r.passed)) {
        return {
          validationId: validation.id,
          status: "pass",
          matchedRequestUrl: request.url,
          urlCheckPassed: true,
          paramResults,
        };
      }
    }
  }

  return failResult(validation, true);
}
