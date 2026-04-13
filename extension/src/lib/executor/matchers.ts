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

export function parseBodyLines(body: string): Map<string, string[]>[] {
  const lines = body.split(/\r?\n/).filter((line) => line.length > 0);
  return lines.map((line) => {
    const params = new Map<string, string[]>();
    const pairs = line.split("&");
    for (const pair of pairs) {
      const eqIndex = pair.indexOf("=");
      if (eqIndex === -1) continue;
      const key = decodeURIComponent(pair.slice(0, eqIndex));
      const value = decodeURIComponent(pair.slice(eqIndex + 1));
      const existing = params.get(key) ?? [];
      existing.push(value);
      params.set(key, existing);
    }
    return params;
  });
}

export function mergeParamMaps(
  base: Map<string, string[]>,
  overlay: Map<string, string[]>,
): Map<string, string[]> {
  const merged = new Map<string, string[]>();
  for (const [key, values] of base) {
    merged.set(key, [...values]);
  }
  for (const [key, values] of overlay) {
    const existing = merged.get(key) ?? [];
    merged.set(key, [...existing, ...values]);
  }
  return merged;
}

const GA4_ITEM_KEY_RE = /^pr(\d+)$/;

const GA4_KNOWN_PREFIXES = [
  "id", "nm", "ln", "va", "lo", "qt", "lp", "pr", "br",
  "ca", "c2", "c3", "c4", "c5", "ds",
];

function parseGA4ItemValue(
  prKey: string,
  raw: string,
): Map<string, string[]> {
  const result = new Map<string, string[]>();
  const tokens = raw.split("~");

  const customKeys = new Map<string, string>();
  const customValues = new Map<string, string>();

  for (const token of tokens) {
    const knownMatch = GA4_KNOWN_PREFIXES.find((p) => token.startsWith(p));
    if (knownMatch) {
      const value = token.slice(knownMatch.length);
      result.set(`${prKey}.${knownMatch}`, [value]);
      continue;
    }

    const cdKeyMatch = token.match(/^k(\d+)(.*)$/);
    if (cdKeyMatch) {
      customKeys.set(cdKeyMatch[1], cdKeyMatch[2]);
      continue;
    }

    const cdValMatch = token.match(/^v(\d+)(.*)$/);
    if (cdValMatch) {
      customValues.set(cdValMatch[1], cdValMatch[2]);
      continue;
    }
  }

  for (const [index, keyName] of customKeys) {
    const value = customValues.get(index);
    if (value !== undefined && keyName.length > 0) {
      result.set(`${prKey}.${keyName}`, [value]);
    }
  }

  return result;
}

export function parseGA4Items(
  params: Map<string, string[]>,
): Map<string, string[]> {
  const expanded = new Map<string, string[]>();

  for (const [key, values] of params) {
    if (GA4_ITEM_KEY_RE.test(key) && values.length > 0) {
      const itemParams = parseGA4ItemValue(key, values[0]);
      for (const [itemKey, itemValues] of itemParams) {
        expanded.set(itemKey, itemValues);
      }
    }
  }

  return expanded;
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
