import type { ParamCheckResult } from "./types";

interface UrlCheckLike {
  match: string;
  value?: string;
}

interface ParamCheckLike {
  key: string;
  match: string;
  value?: string;
}

function checkMatch(
  matchType: string,
  expected: string | undefined,
  actual: string,
): boolean {
  switch (matchType) {
    case "exists":
      return true;
    case "exact":
      return actual === expected;
    case "contains":
      return actual.includes(expected!);
    case "startsWith":
      return actual.startsWith(expected!);
    case "endsWith":
      return actual.endsWith(expected!);
    case "regex":
      return new RegExp(expected!).test(actual);
    default:
      return false;
  }
}

export function checkUrlMatch(
  urlCheck: UrlCheckLike,
  requestUrl: string,
): boolean {
  if (urlCheck.match === "exists") return true;

  const urlWithoutQuery = requestUrl.split("?")[0];
  return (
    checkMatch(urlCheck.match, urlCheck.value, requestUrl) ||
    checkMatch(urlCheck.match, urlCheck.value, urlWithoutQuery)
  );
}

export function parseQueryParams(url: string): Map<string, string[]> {
  const params = new Map<string, string[]>();
  try {
    const urlObj = new URL(url);
    for (const [key, value] of urlObj.searchParams.entries()) {
      const existing = params.get(key) ?? [];
      existing.push(value);
      params.set(key, existing);
    }
  } catch {
    // malformed URL — return empty
  }
  return params;
}

export function checkParamMatch(
  paramCheck: ParamCheckLike,
  params: Map<string, string[]>,
): ParamCheckResult {
  const values = params.get(paramCheck.key);

  if (!values || values.length === 0) {
    return {
      key: paramCheck.key,
      match: paramCheck.match,
      expected: paramCheck.value,
      actual: undefined,
      passed: false,
    };
  }

  if (paramCheck.match === "exists") {
    return {
      key: paramCheck.key,
      match: paramCheck.match,
      actual: values[0],
      passed: true,
    };
  }

  for (const actual of values) {
    if (checkMatch(paramCheck.match, paramCheck.value, actual)) {
      return {
        key: paramCheck.key,
        match: paramCheck.match,
        expected: paramCheck.value,
        actual,
        passed: true,
      };
    }
  }

  return {
    key: paramCheck.key,
    match: paramCheck.match,
    expected: paramCheck.value,
    actual: values[0],
    passed: false,
  };
}
