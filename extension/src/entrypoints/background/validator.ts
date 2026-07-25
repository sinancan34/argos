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

/**
 * A captured request that survived provider/URL matching, paired with the param
 * sets it was matched on. The sets are computed once and reused for the rule's
 * own param checks so a POST body is never parsed twice.
 */
interface RequestCandidate {
  readonly request: CapturedRequest;
  readonly paramSets: ReadonlyArray<Map<string, string[]>>;
}

function getCandidates(
  validation: Validation,
  capturedRequests: CapturedRequest[],
): RequestCandidate[] {
  const provider = validation.provider ?? "custom";
  const isGA4 = provider === "google_analytics";

  if (provider === "custom") {
    if (!validation.url) return [];
    return capturedRequests
      .filter((req) => checkUrlMatch(validation.url!, req.url))
      .map((request) => ({
        request,
        paramSets: buildParamSets(request, isGA4),
      }));
  }

  const providerDef = PROVIDERS[provider];
  if (!providerDef) return [];

  const constraints = providerDef.paramConstraints ?? [];

  const candidates: RequestCandidate[] = [];

  for (const request of capturedRequests) {
    const urlMatches = providerDef.urlPatterns.some((pattern) =>
      new RegExp(pattern).test(request.url),
    );
    if (!urlMatches) continue;

    const paramSets = buildParamSets(request, isGA4);

    // Identification params (GA4's v/tid) travel in the payload on POST hits,
    // so the constraints are checked against the same URL+body param sets the
    // rule itself is evaluated on — a URL-only check drops every such request.
    const qualifies =
      constraints.length === 0 ||
      paramSets.some((params) =>
        constraints.every((c) => checkParamMatch(c, params).passed),
      );

    if (qualifies) candidates.push({ request, paramSets });
  }

  return candidates;
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

/**
 * No request even reached the param checks, so there are no observed values to
 * report — every param is rendered as "not found".
 */
function noRequestResult(validation: Validation): ValidationResult {
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

function passedCount(paramResults: ParamCheckResult[]): number {
  return paramResults.filter((r) => r.passed).length;
}

export function evaluateValidation(
  validation: Validation,
  capturedRequests: CapturedRequest[],
): ValidationResult {
  const candidates = getCandidates(validation, capturedRequests);

  if (candidates.length === 0) {
    return noRequestResult(validation);
  }

  // Best near-miss so far, kept so a failure can report what was actually seen
  // instead of a synthesized all-undefined result.
  let closest: { url: string; paramResults: ParamCheckResult[] } | null = null;

  for (const { request, paramSets } of candidates) {
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

      if (
        closest === null ||
        passedCount(paramResults) > passedCount(closest.paramResults)
      ) {
        closest = { url: request.url, paramResults };
      }
    }
  }

  return {
    validationId: validation.id,
    status: "fail",
    ...(closest ? { matchedRequestUrl: closest.url } : {}),
    urlCheckPassed: true,
    paramResults: closest?.paramResults ?? [],
  };
}
