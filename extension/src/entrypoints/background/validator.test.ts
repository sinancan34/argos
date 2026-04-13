import { describe, it, expect, vi } from "vitest";

vi.mock("@/lib/validation-registry", () => ({
  PROVIDERS: {
    google_analytics: {
      name: "Google Analytics",
      urlPatterns: [
        "https://(analytics\\.google\\.com|www\\.google\\.com)/(g|ccm)/collect",
      ],
      paramSuggestions: [],
    },
  },
}));

import { evaluateValidation } from "./validator";
import type { CapturedRequest } from "@/lib/executor/types";

function makeValidation(overrides: Record<string, unknown> = {}) {
  return {
    id: "v1",
    provider: "custom" as const,
    url: { match: "contains" as const, value: "example.com" },
    params: [],
    ...overrides,
  };
}

describe("evaluateValidation", () => {
  describe("URL-only requests (backward compatibility)", () => {
    it("passes when URL matches and params match", () => {
      const requests: CapturedRequest[] = [
        { url: "https://example.com/collect?en=page_view&v=2" },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
      expect(result.urlCheckPassed).toBe(true);
    });

    it("fails when URL does not match", () => {
      const requests: CapturedRequest[] = [
        { url: "https://other.com/collect?en=page_view" },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("fail");
      expect(result.urlCheckPassed).toBe(false);
    });

    it("fails when URL matches but params do not", () => {
      const requests: CapturedRequest[] = [
        { url: "https://example.com/collect?en=scroll" },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("fail");
      expect(result.urlCheckPassed).toBe(true);
    });
  });

  describe("requests with body", () => {
    it("finds param in body when not in URL", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect?v=2",
          body: "en=page_view&dl=https%3A%2F%2Fsite.com",
        },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("finds param in URL even when body exists", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect?en=page_view",
          body: "ep.city=istanbul",
        },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("matches any body line in multi-event body", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect?v=2",
          body: "en=view_item_list&ep.city=istanbul\r\nen=view_item_list&ep.city=ankara",
        },
      ];
      const validation = makeValidation({
        params: [
          { key: "en", match: "exact", value: "view_item_list" },
          { key: "ep.city", match: "exact", value: "ankara" },
        ],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("fails when no body line matches all params", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect?v=2",
          body: "en=view_item_list&ep.city=istanbul\r\nen=scroll&ep.city=ankara",
        },
      ];
      const validation = makeValidation({
        params: [
          { key: "en", match: "exact", value: "view_item_list" },
          { key: "ep.city", match: "exact", value: "ankara" },
        ],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("fail");
    });

    it("merges URL params with each body line", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect?tid=G-XXXXX",
          body: "en=page_view",
        },
      ];
      const validation = makeValidation({
        params: [
          { key: "tid", match: "startsWith", value: "G-" },
          { key: "en", match: "exact", value: "page_view" },
        ],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });
  });

  describe("GA4 provider with item parsing", () => {
    const ga4Url =
      "https://analytics.google.com/g/collect?v=2&tid=G-XXXXX";

    function makeGA4Validation(params: Record<string, unknown>[]) {
      return makeValidation({
        provider: "google_analytics",
        url: undefined,
        params,
      });
    }

    it("expands pr1 item fields from URL params", () => {
      const requests: CapturedRequest[] = [
        {
          url: `${ga4Url}&en=select_item&pr1=idABC~nmbarista~lnilan-listeleme~qt1~lp1`,
        },
      ];
      const validation = makeGA4Validation([
        { key: "en", match: "exact", value: "select_item" },
        { key: "pr1.nm", match: "exact", value: "barista" },
        { key: "pr1.lp", match: "exact", value: "1" },
      ]);
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("expands pr1 item fields from body", () => {
      const requests: CapturedRequest[] = [
        {
          url: ga4Url,
          body: "en=view_item_list&pr1=idABC~nmbarista~lnilan-listeleme~qt1~lp1",
        },
      ];
      const validation = makeGA4Validation([
        { key: "en", match: "exact", value: "view_item_list" },
        { key: "pr1.nm", match: "exact", value: "barista" },
      ]);
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("expands custom dimensions from pr1", () => {
      const requests: CapturedRequest[] = [
        {
          url: ga4Url,
          body: "en=view_item_list&pr1=k0search_id~v0abc123~idXYZ~nmtest",
        },
      ];
      const validation = makeGA4Validation([
        { key: "pr1.search_id", match: "exact", value: "abc123" },
        { key: "pr1.nm", match: "exact", value: "test" },
      ]);
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("handles multiple items (pr1, pr2) in body", () => {
      const requests: CapturedRequest[] = [
        {
          url: ga4Url,
          body: "en=view_item_list&pr1=nmbarista~lp1&pr2=nmfitness~lp2",
        },
      ];
      const v1 = makeGA4Validation([
        { key: "pr1.nm", match: "exact", value: "barista" },
      ]);
      const v2 = makeGA4Validation([
        { key: "pr2.nm", match: "exact", value: "fitness" },
      ]);
      expect(evaluateValidation(v1, requests).status).toBe("pass");
      expect(evaluateValidation(v2, requests).status).toBe("pass");
    });

    it("matches correct event line in multi-event body", () => {
      const requests: CapturedRequest[] = [
        {
          url: ga4Url,
          body: [
            "en=view_item_list&pr1=nmbarista~lp1&ep.city=istanbul",
            "en=view_item_list&pr1=nmfitness~lp2&ep.city=ankara",
          ].join("\r\n"),
        },
      ];
      const validation = makeGA4Validation([
        { key: "en", match: "exact", value: "view_item_list" },
        { key: "pr1.nm", match: "exact", value: "fitness" },
        { key: "ep.city", match: "exact", value: "ankara" },
      ]);
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("pass");
    });

    it("does not expand items for non-GA4 provider", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect?pr1=nmbarista~lp1&en=test",
        },
      ];
      const validation = makeValidation({
        params: [
          { key: "pr1.nm", match: "exact", value: "barista" },
        ],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.status).toBe("fail");
    });
  });
});
