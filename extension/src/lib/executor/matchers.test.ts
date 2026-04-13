import { describe, it, expect } from "vitest";
import {
  checkUrlMatch,
  parseQueryParams,
  checkParamMatch,
  parseBodyLines,
  mergeParamMaps,
  parseGA4Items,
} from "./matchers";

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

describe("parseBodyLines", () => {
  it("parses single line body", () => {
    const lines = parseBodyLines("en=page_view&dl=https%3A%2F%2Fexample.com");
    expect(lines).toHaveLength(1);
    expect(lines[0].get("en")).toEqual(["page_view"]);
    expect(lines[0].get("dl")).toEqual(["https://example.com"]);
  });

  it("parses multi-line body with \\r\\n separators", () => {
    const body =
      "en=view_item_list&ep.city=istanbul\r\nen=view_item_list&ep.city=ankara";
    const lines = parseBodyLines(body);
    expect(lines).toHaveLength(2);
    expect(lines[0].get("ep.city")).toEqual(["istanbul"]);
    expect(lines[1].get("ep.city")).toEqual(["ankara"]);
  });

  it("parses multi-line body with \\n separators", () => {
    const body = "en=event_a&v=1\nen=event_b&v=2";
    const lines = parseBodyLines(body);
    expect(lines).toHaveLength(2);
    expect(lines[0].get("en")).toEqual(["event_a"]);
    expect(lines[1].get("en")).toEqual(["event_b"]);
  });

  it("skips empty lines", () => {
    const body = "en=page_view\r\n\r\nen=scroll\r\n";
    const lines = parseBodyLines(body);
    expect(lines).toHaveLength(2);
  });

  it("returns empty array for empty body", () => {
    expect(parseBodyLines("")).toHaveLength(0);
  });

  it("handles URL-encoded values in body", () => {
    const body = "dl=https%3A%2F%2Fexample.com%2Fpath&dt=My%20Page";
    const lines = parseBodyLines(body);
    expect(lines[0].get("dl")).toEqual(["https://example.com/path"]);
    expect(lines[0].get("dt")).toEqual(["My Page"]);
  });
});

describe("mergeParamMaps", () => {
  it("merges two non-overlapping maps", () => {
    const base = new Map([["a", ["1"]]]);
    const overlay = new Map([["b", ["2"]]]);
    const merged = mergeParamMaps(base, overlay);
    expect(merged.get("a")).toEqual(["1"]);
    expect(merged.get("b")).toEqual(["2"]);
  });

  it("combines values for overlapping keys", () => {
    const base = new Map([["a", ["1"]]]);
    const overlay = new Map([["a", ["2"]]]);
    const merged = mergeParamMaps(base, overlay);
    expect(merged.get("a")).toEqual(["1", "2"]);
  });

  it("does not mutate original maps", () => {
    const base = new Map([["a", ["1"]]]);
    const overlay = new Map([["a", ["2"]]]);
    mergeParamMaps(base, overlay);
    expect(base.get("a")).toEqual(["1"]);
    expect(overlay.get("a")).toEqual(["2"]);
  });
});

describe("parseGA4Items", () => {
  it("expands known item prefixes from pr1", () => {
    const params = new Map([
      ["pr1", ["idABC123~nmbarista~lnilan-listeleme~loistanbul~qt1~lp1"]],
    ]);
    const expanded = parseGA4Items(params);
    expect(expanded.get("pr1.id")).toEqual(["ABC123"]);
    expect(expanded.get("pr1.nm")).toEqual(["barista"]);
    expect(expanded.get("pr1.ln")).toEqual(["ilan-listeleme"]);
    expect(expanded.get("pr1.lo")).toEqual(["istanbul"]);
    expect(expanded.get("pr1.qt")).toEqual(["1"]);
    expect(expanded.get("pr1.lp")).toEqual(["1"]);
  });

  it("expands custom dimensions from k/v pairs", () => {
    const params = new Map([
      ["pr1", ["k0search_id~v0abc123~idXYZ"]],
    ]);
    const expanded = parseGA4Items(params);
    expect(expanded.get("pr1.search_id")).toEqual(["abc123"]);
    expect(expanded.get("pr1.id")).toEqual(["XYZ"]);
  });

  it("handles multiple items (pr1, pr2)", () => {
    const params = new Map([
      ["pr1", ["nmbarista~lp1"]],
      ["pr2", ["nmfitness~lp2"]],
    ]);
    const expanded = parseGA4Items(params);
    expect(expanded.get("pr1.nm")).toEqual(["barista"]);
    expect(expanded.get("pr1.lp")).toEqual(["1"]);
    expect(expanded.get("pr2.nm")).toEqual(["fitness"]);
    expect(expanded.get("pr2.lp")).toEqual(["2"]);
  });

  it("ignores non-pr keys", () => {
    const params = new Map([
      ["en", ["page_view"]],
      ["tid", ["G-XXXXX"]],
    ]);
    const expanded = parseGA4Items(params);
    expect(expanded.size).toBe(0);
  });

  it("handles real GA4 item value with all fields", () => {
    const raw =
      "k0search_id~v0cadi2zeud12x5p275zrzaodyv7kfpcyo~idF63F4E7109CA4192865B9CE78C0AC767~nmbarista~lnilan-listeleme~vailan~loistanbul~qt1~lp1";
    const params = new Map([["pr1", [raw]]]);
    const expanded = parseGA4Items(params);
    expect(expanded.get("pr1.search_id")).toEqual([
      "cadi2zeud12x5p275zrzaodyv7kfpcyo",
    ]);
    expect(expanded.get("pr1.id")).toEqual(["F63F4E7109CA4192865B9CE78C0AC767"]);
    expect(expanded.get("pr1.nm")).toEqual(["barista"]);
    expect(expanded.get("pr1.ln")).toEqual(["ilan-listeleme"]);
    expect(expanded.get("pr1.va")).toEqual(["ilan"]);
    expect(expanded.get("pr1.lo")).toEqual(["istanbul"]);
    expect(expanded.get("pr1.qt")).toEqual(["1"]);
    expect(expanded.get("pr1.lp")).toEqual(["1"]);
  });

  it("handles custom dimension with missing value pair", () => {
    const params = new Map([["pr1", ["k0mykey~nmtest"]]]);
    const expanded = parseGA4Items(params);
    expect(expanded.get("pr1.nm")).toEqual(["test"]);
    expect(expanded.has("pr1.mykey")).toBe(false);
  });
});
