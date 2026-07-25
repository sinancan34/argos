import { describe, it, expect, vi } from "vitest";

vi.mock("@/lib/validation-registry", () => ({
  PROVIDERS: {
    google_analytics: {
      name: "Google Analytics",
      urlPatterns: ["^https?://[^/]+/g/collect"],
      paramConstraints: [
        { key: "v", match: "exact", value: "2" },
        { key: "tid", match: "startsWith", value: "G-" },
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

  describe("GA4 provider host-agnostic path matching", () => {
    function makeGA4PathValidation() {
      return makeValidation({
        provider: "google_analytics",
        url: undefined,
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
    }

    it("matches /g/collect on the canonical google-analytics.com host", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect?v=2&tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4PathValidation(), requests);
      expect(result.status).toBe("pass");
    });

    it("matches /g/collect on a first-party host (host-agnostic)", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://metrics.example.com/g/collect?v=2&tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4PathValidation(), requests);
      expect(result.status).toBe("pass");
    });

    it("does not match the /ccm/collect endpoint", () => {
      const requests: CapturedRequest[] = [
        { url: "https://www.google.com/ccm/collect?v=2&en=page_view" },
      ];
      const result = evaluateValidation(makeGA4PathValidation(), requests);
      expect(result.status).toBe("fail");
    });

    it("does not match /g/collect below the path root", () => {
      const requests: CapturedRequest[] = [
        { url: "https://foo.com/api/g/collect?v=2&en=page_view" },
      ];
      const result = evaluateValidation(makeGA4PathValidation(), requests);
      expect(result.status).toBe("fail");
    });
  });

  describe("GA4 provider identification constraints (v=2, tid=G-)", () => {
    function makeGA4ConstraintValidation() {
      return makeValidation({
        provider: "google_analytics",
        url: undefined,
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
    }

    it("passes when both v=2 and tid starts with G-", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect?v=2&tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("pass");
    });

    it("does not match when v is not 2 (e.g. Universal Analytics v=1)", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect?v=1&tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("fail");
    });

    it("does not match when tid does not start with G- (e.g. UA-)", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect?v=2&tid=UA-123&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("fail");
    });

    it("does not match when tid is missing", () => {
      const requests: CapturedRequest[] = [
        { url: "https://www.google-analytics.com/g/collect?v=2&en=page_view" },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("fail");
    });

    it("does not match when v is missing", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect?tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("fail");
    });
  });

  describe("GA4 provider constraints satisfied from the POST body", () => {
    function makeGA4ConstraintValidation() {
      return makeValidation({
        provider: "google_analytics",
        url: undefined,
        params: [{ key: "en", match: "exact", value: "page_view" }],
      });
    }

    it("matches when v and tid live only in the body", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect",
          body: "v=2&tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("pass");
    });

    it("matches when v is in the URL and tid only in the body", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect?v=2",
          body: "tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("pass");
    });

    it("matches the body line that satisfies both constraints and params", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect",
          body: "v=2&tid=G-XXXXX&en=scroll\r\nv=2&tid=G-XXXXX&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.status).toBe("pass");
    });

    it("does not match when the body carries a non-GA4 tid", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect",
          body: "v=2&tid=UA-123&en=page_view",
        },
      ];
      const result = evaluateValidation(makeGA4ConstraintValidation(), requests);
      expect(result.urlCheckPassed).toBe(false);
    });
  });

  describe("failure diagnostics", () => {
    it("reports the observed value when a param has the wrong value", () => {
      const requests: CapturedRequest[] = [
        { url: "https://example.com/collect?en=view_item" },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "purchase" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.paramResults[0].actual).toBe("view_item");
    });

    it("reports the observed value from a POST body", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://www.google-analytics.com/g/collect",
          body: "v=2&tid=G-XXXXX&en=view_item",
        },
      ];
      const validation = makeValidation({
        provider: "google_analytics",
        url: undefined,
        params: [{ key: "en", match: "exact", value: "purchase" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.paramResults[0].actual).toBe("view_item");
    });

    it("exposes the request it evaluated when params do not match", () => {
      const requests: CapturedRequest[] = [
        { url: "https://example.com/collect?en=view_item" },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "purchase" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.matchedRequestUrl).toBe(
        "https://example.com/collect?en=view_item",
      );
    });

    it("keeps actual undefined when no request matched at all", () => {
      const requests: CapturedRequest[] = [
        { url: "https://other.com/collect?en=view_item" },
      ];
      const validation = makeValidation({
        params: [{ key: "en", match: "exact", value: "purchase" }],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.paramResults[0].actual).toBeUndefined();
    });

    it("picks the param set with the most passing checks", () => {
      const requests: CapturedRequest[] = [
        {
          url: "https://example.com/collect",
          body: "en=scroll&id=wrong\r\nen=purchase&id=wrong",
        },
      ];
      const validation = makeValidation({
        params: [
          { key: "en", match: "exact", value: "purchase" },
          { key: "id", match: "exact", value: "right" },
        ],
      });
      const result = evaluateValidation(validation, requests);
      expect(result.paramResults[0].actual).toBe("purchase");
    });
  });
});
