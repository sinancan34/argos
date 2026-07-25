import { describe, it, expect } from "vitest";
import {
  scenarioCreateSchema,
  scenarioUpdateSchema,
  matchTypeValues,
  providerValues,
} from "./scenario";

const DEVICE_ID = "5b1f0d2e-0000-4000-8000-000000000000";
const NAME_MAX_LENGTH = 500;
const DEFAULT_STEP_TIMEOUT = 5000;
const DEFAULT_VALIDATION_TIMEOUT = 10000;
const LONG_STRING_LENGTH = 10000;

const PARAM_VALUE_REQUIRED_MESSAGE =
  "Value is required when match type is not 'exists'";
const CUSTOM_URL_REQUIRED_MESSAGE =
  "URL check is required when provider is 'Custom URL'";

type ScenarioCreateInput = Record<string, unknown>;

/** Minimal valid create payload; override individual fields per test. */
function makeCreateInput(
  overrides: ScenarioCreateInput = {},
): ScenarioCreateInput {
  return {
    name: "Checkout flow",
    device_id: DEVICE_ID,
    steps: [
      { id: "step-1", command: "goto", params: { url: "https://example.com" } },
    ],
    validations: [
      {
        id: "validation-1",
        provider: "google_analytics",
        params: [{ key: "en", match: "exact", value: "page_view" }],
      },
    ],
    ...overrides,
  };
}

/** First issue message from a failed parse, for exact-message assertions. */
function firstIssueMessage(input: unknown): string {
  const result = scenarioCreateSchema.safeParse(input);
  if (result.success) throw new Error("expected parse to fail");
  return result.error.issues[0].message;
}

describe("matchTypeValues", () => {
  it("exposes every match type from shared/commands.json", () => {
    // Arrange — sourced from the shared registry

    // Act
    const values = matchTypeValues;

    // Assert
    expect(values).toEqual([
      "exact",
      "contains",
      "startsWith",
      "endsWith",
      "regex",
      "exists",
    ]);
  });
});

describe("providerValues", () => {
  it("puts custom first, then the shared provider keys", () => {
    // Arrange — derived from shared/providers.json keys

    // Act
    const values = providerValues;

    // Assert
    expect(values).toEqual(["custom", "google_analytics"]);
  });
});

describe("scenarioCreateSchema — happy path", () => {
  it("parses a minimal valid payload", () => {
    // Arrange
    const input = makeCreateInput();

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("Checkout flow");
  });

  it("parses a fully populated payload", () => {
    // Arrange
    const input = makeCreateInput({
      description: "Validates the GA4 page_view on checkout",
      status: false,
      step_timeout: 3000,
      validation_timeout: 8000,
      steps: [
        {
          id: "step-1",
          command: "goto",
          params: { url: "https://example.com" },
        },
        { id: "step-2", command: "click", params: { selector: "#buy" } },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps).toHaveLength(2);
  });

  it("accepts a custom provider validation carrying its own url check", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "custom",
          url: { match: "contains", value: "/collect" },
          params: [],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].url).toEqual({
      match: "contains",
      value: "/collect",
    });
  });

  it("strips unknown top-level keys", () => {
    // Arrange
    const input = makeCreateInput({ unexpected: "drop me" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed).not.toHaveProperty("unexpected");
  });

  it("does not mutate the input object", () => {
    // Arrange
    const input = makeCreateInput();
    const snapshot = structuredClone(input);

    // Act
    scenarioCreateSchema.parse(input);

    // Assert
    expect(input).toEqual(snapshot);
  });
});

describe("scenarioCreateSchema — defaults", () => {
  it("defaults status to true when omitted", () => {
    // Arrange
    const input = makeCreateInput();

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.status).toBe(true);
  });

  it("preserves an explicit status of false", () => {
    // Arrange
    const input = makeCreateInput({ status: false });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.status).toBe(false);
  });

  it("defaults step_timeout to the shared registry default", () => {
    // Arrange
    const input = makeCreateInput();

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.step_timeout).toBe(DEFAULT_STEP_TIMEOUT);
  });

  it("defaults validation_timeout to the shared registry default", () => {
    // Arrange
    const input = makeCreateInput();

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validation_timeout).toBe(DEFAULT_VALIDATION_TIMEOUT);
  });

  it("defaults a step's params to an empty object", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ id: "step-1", command: "goto" }],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps[0].params).toEqual({});
  });

  it("defaults a validation's params to an empty array", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [{ id: "validation-1", provider: "google_analytics" }],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params).toEqual([]);
  });

  it("leaves description undefined when omitted", () => {
    // Arrange
    const input = makeCreateInput();

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.description).toBeUndefined();
  });
});

describe("scenarioCreateSchema — name", () => {
  it("rejects an empty name", () => {
    // Arrange
    const input = makeCreateInput({ name: "" });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts a single-character name at the lower boundary", () => {
    // Arrange
    const input = makeCreateInput({ name: "a" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("a");
  });

  it("accepts a name at the maximum length", () => {
    // Arrange
    const input = makeCreateInput({ name: "a".repeat(NAME_MAX_LENGTH) });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toHaveLength(NAME_MAX_LENGTH);
  });

  it("rejects a name one character over the maximum length", () => {
    // Arrange
    const input = makeCreateInput({ name: "a".repeat(NAME_MAX_LENGTH + 1) });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a very long name", () => {
    // Arrange
    const input = makeCreateInput({ name: "a".repeat(LONG_STRING_LENGTH) });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts a whitespace-only name because it is not trimmed", () => {
    // Arrange — documents that the schema does not trim
    const input = makeCreateInput({ name: "   " });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("   ");
  });

  it("accepts Turkish characters in the name", () => {
    // Arrange
    const input = makeCreateInput({ name: "Ödeme akışı ğüşöçıİ" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("Ödeme akışı ğüşöçıİ");
  });

  it("accepts CJK characters in the name", () => {
    // Arrange
    const input = makeCreateInput({ name: "決済フロー" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("決済フロー");
  });

  it("accepts right-to-left text in the name", () => {
    // Arrange
    const input = makeCreateInput({ name: "تدفق الدفع" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("تدفق الدفع");
  });

  it("accepts emoji in the name", () => {
    // Arrange
    const input = makeCreateInput({ name: "checkout 🛒" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.name).toBe("checkout 🛒");
  });

  it("rejects a missing name", () => {
    // Arrange
    const { name: _name, ...withoutName } = makeCreateInput();

    // Act
    const result = scenarioCreateSchema.safeParse(withoutName);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a null name", () => {
    // Arrange
    const input = makeCreateInput({ name: null });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a numeric name", () => {
    // Arrange
    const input = makeCreateInput({ name: 42 });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });
});

describe("scenarioCreateSchema — device_id", () => {
  it("rejects an empty device_id", () => {
    // Arrange
    const input = makeCreateInput({ device_id: "" });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a missing device_id", () => {
    // Arrange
    const { device_id: _deviceId, ...withoutDevice } = makeCreateInput();

    // Act
    const result = scenarioCreateSchema.safeParse(withoutDevice);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts any non-empty string because the format is not validated", () => {
    // Arrange — documents that device_id is not checked against a UUID shape
    const input = makeCreateInput({ device_id: "not-a-uuid" });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.device_id).toBe("not-a-uuid");
  });

  it("rejects a null device_id", () => {
    // Arrange
    const input = makeCreateInput({ device_id: null });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });
});

describe("scenarioCreateSchema — timeouts", () => {
  it("accepts 1 as the smallest positive step_timeout", () => {
    // Arrange
    const input = makeCreateInput({ step_timeout: 1 });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.step_timeout).toBe(1);
  });

  it("rejects a step_timeout of zero", () => {
    // Arrange
    const input = makeCreateInput({ step_timeout: 0 });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a negative step_timeout", () => {
    // Arrange
    const input = makeCreateInput({ step_timeout: -1 });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects negative zero as a step_timeout", () => {
    // Arrange — -0 is not positive
    const input = makeCreateInput({ step_timeout: -0 });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a fractional step_timeout", () => {
    // Arrange
    const input = makeCreateInput({ step_timeout: 100.5 });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects NaN as a step_timeout", () => {
    // Arrange
    const input = makeCreateInput({ step_timeout: NaN });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects Infinity as a step_timeout", () => {
    // Arrange
    const input = makeCreateInput({ step_timeout: Infinity });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a numeric string as a step_timeout", () => {
    // Arrange — no coercion is configured
    const input = makeCreateInput({ step_timeout: "5000" });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts MAX_SAFE_INTEGER as a validation_timeout", () => {
    // Arrange — no upper bound is configured
    const input = makeCreateInput({
      validation_timeout: Number.MAX_SAFE_INTEGER,
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validation_timeout).toBe(Number.MAX_SAFE_INTEGER);
  });

  it("rejects MIN_SAFE_INTEGER as a validation_timeout", () => {
    // Arrange
    const input = makeCreateInput({
      validation_timeout: Number.MIN_SAFE_INTEGER,
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });
});

describe("scenarioCreateSchema — steps", () => {
  it("rejects an empty steps array", () => {
    // Arrange
    const input = makeCreateInput({ steps: [] });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts a single step at the minimum boundary", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ id: "step-1", command: "click", params: { selector: "#a" } }],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps).toHaveLength(1);
  });

  it("accepts the goto command", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ id: "step-1", command: "goto", params: {} }],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps[0].command).toBe("goto");
  });

  it("accepts the click command", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ id: "step-1", command: "click", params: {} }],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps[0].command).toBe("click");
  });

  it("rejects an unknown command", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ id: "step-1", command: "scroll", params: {} }],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a command whose case does not match", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ id: "step-1", command: "GOTO", params: {} }],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a step without an id", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [{ command: "goto", params: {} }],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts an empty step id because no minimum length is set", () => {
    // Arrange — documents that step ids are unconstrained strings
    const input = makeCreateInput({
      steps: [{ id: "", command: "goto", params: {} }],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps[0].id).toBe("");
  });

  it("keeps arbitrary param values because params is an unknown record", () => {
    // Arrange
    const input = makeCreateInput({
      steps: [
        { id: "step-1", command: "goto", params: { url: 42, nested: { a: 1 } } },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.steps[0].params).toEqual({ url: 42, nested: { a: 1 } });
  });

  it("rejects steps that are not an array", () => {
    // Arrange
    const input = makeCreateInput({ steps: "goto" });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });
});

describe("scenarioCreateSchema — validations", () => {
  it("rejects an empty validations array", () => {
    // Arrange
    const input = makeCreateInput({ validations: [] });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects an unknown provider", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [{ id: "validation-1", provider: "facebook_pixel" }],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a validation with no provider", () => {
    // Arrange — provider is mandatory, with no default on the request schema
    const input = makeCreateInput({
      validations: [{ id: "validation-1", params: [] }],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a custom provider without a url check", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [{ id: "validation-1", provider: "custom", params: [] }],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("reports the custom-provider url requirement message", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [{ id: "validation-1", provider: "custom", params: [] }],
    });

    // Act
    const message = firstIssueMessage(input);

    // Assert
    expect(message).toBe(CUSTOM_URL_REQUIRED_MESSAGE);
  });

  it("allows a non-custom provider without a url check", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        { id: "validation-1", provider: "google_analytics", params: [] },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].url).toBeUndefined();
  });

  it("allows a non-custom provider that also carries a url check", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          url: { match: "exists" },
          params: [],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].url).toEqual({ match: "exists" });
  });
});

describe("scenarioCreateSchema — url check", () => {
  it("accepts match=exists with no value", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "custom",
          url: { match: "exists" },
          params: [],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].url?.value).toBeUndefined();
  });

  it("rejects match=contains with no value", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "custom",
          url: { match: "contains" },
          params: [],
        },
      ],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects match=contains with an empty value", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "custom",
          url: { match: "contains", value: "" },
          params: [],
        },
      ],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("reports the conditional value message for a url check", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "custom",
          url: { match: "regex" },
          params: [],
        },
      ],
    });

    // Act
    const message = firstIssueMessage(input);

    // Assert
    expect(message).toBe(PARAM_VALUE_REQUIRED_MESSAGE);
  });

  it("rejects an unknown url match type", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "custom",
          url: { match: "fuzzy", value: "x" },
          params: [],
        },
      ],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });
});

describe("scenarioCreateSchema — param checks", () => {
  it.each(["exact", "contains", "startsWith", "endsWith", "regex"] as const)(
    "requires a value for match=%s",
    (match) => {
      // Arrange
      const input = makeCreateInput({
        validations: [
          {
            id: "validation-1",
            provider: "google_analytics",
            params: [{ key: "en", match }],
          },
        ],
      });

      // Act
      const result = scenarioCreateSchema.safeParse(input);

      // Assert
      expect(result.success).toBe(false);
    },
  );

  it("accepts match=exists with no value", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "en", match: "exists" }],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params[0].value).toBeUndefined();
  });

  it("accepts match=exists that also carries a value", () => {
    // Arrange — the refinement short-circuits on exists
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "en", match: "exists", value: "ignored" }],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params[0].value).toBe("ignored");
  });

  it("reports the conditional value message for a param check", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "en", match: "exact" }],
        },
      ],
    });

    // Act
    const message = firstIssueMessage(input);

    // Assert
    expect(message).toBe(PARAM_VALUE_REQUIRED_MESSAGE);
  });

  it("rejects an empty param key", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "", match: "exists" }],
        },
      ],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts a GA4 item dot-notation key", () => {
    // Arrange — keys like pr1.nm address parsed GA4 item tokens
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "pr1.nm", match: "exact", value: "barista" }],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params[0].key).toBe("pr1.nm");
  });

  it("accepts a whitespace-only param value", () => {
    // Arrange — length 1 satisfies the conditional minimum
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "en", match: "exact", value: " " }],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params[0].value).toBe(" ");
  });

  it("accepts a very long param value", () => {
    // Arrange — no maximum length is configured
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [
            { key: "en", match: "exact", value: "a".repeat(LONG_STRING_LENGTH) },
          ],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params[0].value).toHaveLength(
      LONG_STRING_LENGTH,
    );
  });

  it("accepts multiple param checks on one validation", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [
            { key: "en", match: "exact", value: "page_view" },
            { key: "tid", match: "startsWith", value: "G-" },
          ],
        },
      ],
    });

    // Act
    const parsed = scenarioCreateSchema.parse(input);

    // Assert
    expect(parsed.validations[0].params).toHaveLength(2);
  });

  it("rejects a null param value", () => {
    // Arrange
    const input = makeCreateInput({
      validations: [
        {
          id: "validation-1",
          provider: "google_analytics",
          params: [{ key: "en", match: "exact", value: null }],
        },
      ],
    });

    // Act
    const result = scenarioCreateSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });
});

describe("scenarioCreateSchema — invalid top-level input", () => {
  it("rejects null", () => {
    // Arrange — null is not an object

    // Act
    const result = scenarioCreateSchema.safeParse(null);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects undefined", () => {
    // Arrange — a payload is required

    // Act
    const result = scenarioCreateSchema.safeParse(undefined);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects an empty object", () => {
    // Arrange — required fields are missing

    // Act
    const result = scenarioCreateSchema.safeParse({});

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects an array", () => {
    // Arrange — an array is not a scenario object

    // Act
    const result = scenarioCreateSchema.safeParse([]);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a string", () => {
    // Arrange — a primitive is not a scenario object

    // Act
    const result = scenarioCreateSchema.safeParse("scenario");

    // Assert
    expect(result.success).toBe(false);
  });

  it("throws a ZodError from parse on invalid input", () => {
    // Arrange — parse throws where safeParse reports

    // Act & Assert
    expect(() => scenarioCreateSchema.parse({})).toThrow();
  });
});

describe("scenarioUpdateSchema", () => {
  it("accepts an empty patch", () => {
    // Arrange — every field is optional

    // Act
    const result = scenarioUpdateSchema.safeParse({});

    // Assert
    expect(result.success).toBe(true);
  });

  it("does not inject the status default", () => {
    // Arrange — status is declared optional with no default on the update schema

    // Act
    const parsed = scenarioUpdateSchema.parse({});

    // Assert
    expect(parsed.status).toBeUndefined();
  });

  it("leaves name undefined when absent", () => {
    // Arrange — buildStringSchema carries no default, so optional means absent

    // Act
    const parsed = scenarioUpdateSchema.parse({});

    // Assert
    expect(parsed.name).toBeUndefined();
  });

  // The two tests below pin down surprising behavior rather than desired behavior:
  // buildIntSchema applies `.default(...)`, and in Zod 4 `.default(x).optional()`
  // still substitutes the default for an absent key. An otherwise-empty patch
  // therefore carries both timeouts, so a PATCH that only means to rename a
  // scenario also rewrites step_timeout and validation_timeout to the defaults.
  it("injects the step_timeout default even for an absent key", () => {
    // Arrange — `.default().optional()` does not short-circuit on undefined

    // Act
    const parsed = scenarioUpdateSchema.parse({});

    // Assert
    expect(parsed.step_timeout).toBe(DEFAULT_STEP_TIMEOUT);
  });

  it("injects the validation_timeout default even for an absent key", () => {
    // Arrange — same `.default().optional()` interaction as step_timeout

    // Act
    const parsed = scenarioUpdateSchema.parse({});

    // Assert
    expect(parsed.validation_timeout).toBe(DEFAULT_VALIDATION_TIMEOUT);
  });

  it("accepts a name-only patch", () => {
    // Arrange
    const patch = { name: "Renamed" };

    // Act
    const parsed = scenarioUpdateSchema.parse(patch);

    // Assert
    expect(parsed.name).toBe("Renamed");
  });

  it("accepts a status-only patch of false", () => {
    // Arrange
    const patch = { status: false };

    // Act
    const parsed = scenarioUpdateSchema.parse(patch);

    // Assert
    expect(parsed.status).toBe(false);
  });

  it("still enforces the name minimum length when name is present", () => {
    // Arrange
    const patch = { name: "" };

    // Act
    const result = scenarioUpdateSchema.safeParse(patch);

    // Assert
    expect(result.success).toBe(false);
  });

  it("still enforces the name maximum length when name is present", () => {
    // Arrange
    const patch = { name: "a".repeat(NAME_MAX_LENGTH + 1) };

    // Act
    const result = scenarioUpdateSchema.safeParse(patch);

    // Assert
    expect(result.success).toBe(false);
  });

  it("still enforces a positive step_timeout when present", () => {
    // Arrange
    const patch = { step_timeout: 0 };

    // Act
    const result = scenarioUpdateSchema.safeParse(patch);

    // Assert
    expect(result.success).toBe(false);
  });

  it("still rejects an empty steps array when steps is present", () => {
    // Arrange
    const patch = { steps: [] };

    // Act
    const result = scenarioUpdateSchema.safeParse(patch);

    // Assert
    expect(result.success).toBe(false);
  });

  it("still rejects an empty validations array when validations is present", () => {
    // Arrange
    const patch = { validations: [] };

    // Act
    const result = scenarioUpdateSchema.safeParse(patch);

    // Assert
    expect(result.success).toBe(false);
  });

  it("still enforces the custom-provider url requirement when validations is present", () => {
    // Arrange
    const patch = {
      validations: [{ id: "validation-1", provider: "custom", params: [] }],
    };

    // Act
    const result = scenarioUpdateSchema.safeParse(patch);

    // Assert
    expect(result.success).toBe(false);
  });

  it("accepts a full replacement patch", () => {
    // Arrange
    const patch = {
      name: "Checkout flow",
      description: "updated",
      status: true,
      device_id: DEVICE_ID,
      step_timeout: 2000,
      validation_timeout: 4000,
      steps: [{ id: "step-1", command: "goto", params: {} }],
      validations: [
        { id: "validation-1", provider: "google_analytics", params: [] },
      ],
    };

    // Act
    const parsed = scenarioUpdateSchema.parse(patch);

    // Assert
    expect(parsed.step_timeout).toBe(2000);
  });

  it("rejects null", () => {
    // Arrange — null is not a patch object

    // Act
    const result = scenarioUpdateSchema.safeParse(null);

    // Assert
    expect(result.success).toBe(false);
  });

  it("strips unknown keys", () => {
    // Arrange
    const patch = { unexpected: "drop me" };

    // Act
    const parsed = scenarioUpdateSchema.parse(patch);

    // Assert
    expect(parsed).not.toHaveProperty("unexpected");
  });
});
