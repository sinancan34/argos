import { describe, it, expect } from "vitest";
import { checkUrlMatch, parseQueryParams, checkParamMatch } from "./matchers";

describe("checkUrlMatch", () => {
  it("returns true for exists match type", () => {
    expect(checkUrlMatch({ match: "exists" }, "https://example.com")).toBe(true);
  });

  it("matches exact URL", () => {
    expect(
      checkUrlMatch(
        { match: "exact", value: "https://example.com/path" },
        "https://example.com/path",
      ),
    ).toBe(true);
  });

  it("fails exact match on different URL", () => {
    expect(
      checkUrlMatch(
        { match: "exact", value: "https://example.com" },
        "https://other.com",
      ),
    ).toBe(false);
  });

  it("matches contains in URL", () => {
    expect(
      checkUrlMatch(
        { match: "contains", value: "example" },
        "https://example.com/page",
      ),
    ).toBe(true);
  });

  it("matches startsWith", () => {
    expect(
      checkUrlMatch(
        { match: "startsWith", value: "https://example" },
        "https://example.com/page",
      ),
    ).toBe(true);
  });

  it("matches endsWith on URL without query", () => {
    expect(
      checkUrlMatch(
        { match: "endsWith", value: "/page" },
        "https://example.com/page?foo=bar",
      ),
    ).toBe(true);
  });

  it("matches regex", () => {
    expect(
      checkUrlMatch(
        { match: "regex", value: "example\\.com\\/page" },
        "https://example.com/page",
      ),
    ).toBe(true);
  });

  it("returns false for unknown match type", () => {
    expect(
      checkUrlMatch({ match: "unknown", value: "x" }, "https://example.com"),
    ).toBe(false);
  });

  it("matches against URL without query string too", () => {
    expect(
      checkUrlMatch(
        { match: "exact", value: "https://example.com/path" },
        "https://example.com/path?q=1",
      ),
    ).toBe(true);
  });
});

describe("parseQueryParams", () => {
  it("parses basic query params", () => {
    const params = parseQueryParams("https://example.com?foo=bar&baz=qux");
    expect(params.get("foo")).toEqual(["bar"]);
    expect(params.get("baz")).toEqual(["qux"]);
  });

  it("handles duplicate keys", () => {
    const params = parseQueryParams("https://example.com?a=1&a=2");
    expect(params.get("a")).toEqual(["1", "2"]);
  });

  it("returns empty map for URL without params", () => {
    const params = parseQueryParams("https://example.com");
    expect(params.size).toBe(0);
  });

  it("returns empty map for malformed URL", () => {
    const params = parseQueryParams("not-a-url");
    expect(params.size).toBe(0);
  });

  it("handles empty param values", () => {
    const params = parseQueryParams("https://example.com?key=");
    expect(params.get("key")).toEqual([""]);
  });
});

describe("checkParamMatch", () => {
  const params = parseQueryParams(
    "https://example.com?utm_source=google&tid=UA-123&v=1",
  );

  it("passes exists check when key is present", () => {
    const result = checkParamMatch(
      { key: "utm_source", match: "exists" },
      params,
    );
    expect(result.passed).toBe(true);
    expect(result.actual).toBe("google");
  });

  it("fails exists check when key is missing", () => {
    const result = checkParamMatch(
      { key: "missing", match: "exists" },
      params,
    );
    expect(result.passed).toBe(false);
    expect(result.actual).toBeUndefined();
  });

  it("passes exact match", () => {
    const result = checkParamMatch(
      { key: "utm_source", match: "exact", value: "google" },
      params,
    );
    expect(result.passed).toBe(true);
  });

  it("fails exact match with wrong value", () => {
    const result = checkParamMatch(
      { key: "utm_source", match: "exact", value: "facebook" },
      params,
    );
    expect(result.passed).toBe(false);
    expect(result.expected).toBe("facebook");
    expect(result.actual).toBe("google");
  });

  it("passes contains match", () => {
    const result = checkParamMatch(
      { key: "tid", match: "contains", value: "UA" },
      params,
    );
    expect(result.passed).toBe(true);
  });

  it("passes startsWith match", () => {
    const result = checkParamMatch(
      { key: "tid", match: "startsWith", value: "UA-" },
      params,
    );
    expect(result.passed).toBe(true);
  });

  it("passes endsWith match", () => {
    const result = checkParamMatch(
      { key: "tid", match: "endsWith", value: "123" },
      params,
    );
    expect(result.passed).toBe(true);
  });

  it("passes regex match", () => {
    const result = checkParamMatch(
      { key: "tid", match: "regex", value: "^UA-\\d+$" },
      params,
    );
    expect(result.passed).toBe(true);
  });

  it("fails when key is missing for non-exists match", () => {
    const result = checkParamMatch(
      { key: "nope", match: "exact", value: "x" },
      params,
    );
    expect(result.passed).toBe(false);
    expect(result.actual).toBeUndefined();
  });

  it("checks all values for duplicate keys", () => {
    const multiParams = parseQueryParams(
      "https://example.com?tag=a&tag=b&tag=match",
    );
    const result = checkParamMatch(
      { key: "tag", match: "exact", value: "match" },
      multiParams,
    );
    expect(result.passed).toBe(true);
    expect(result.actual).toBe("match");
  });
});
