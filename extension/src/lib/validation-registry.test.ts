import { describe, it, expect } from "vitest";
import {
  buildStringSchema,
  buildIntSchema,
  buildEnumSchema,
  ENUMS,
  SCENARIO_FIELDS,
  URL_CHECK_FIELDS,
  PARAM_CHECK_FIELDS,
  PROVIDERS,
  PROVIDER_VALUES,
} from "./validation-registry";

describe("buildStringSchema", () => {
  it("creates basic string schema", () => {
    const schema = buildStringSchema({ type: "string" });
    expect(schema.parse("hello")).toBe("hello");
  });

  it("enforces minLength", () => {
    const schema = buildStringSchema({ type: "string", minLength: 3 });
    expect(() => schema.parse("ab")).toThrow();
    expect(schema.parse("abc")).toBe("abc");
  });

  it("enforces maxLength", () => {
    const schema = buildStringSchema({ type: "string", maxLength: 5 });
    expect(() => schema.parse("123456")).toThrow();
    expect(schema.parse("12345")).toBe("12345");
  });

  it("enforces both min and max length", () => {
    const schema = buildStringSchema({
      type: "string",
      minLength: 1,
      maxLength: 500,
    });
    expect(() => schema.parse("")).toThrow();
    expect(schema.parse("valid")).toBe("valid");
  });
});

describe("buildIntSchema", () => {
  it("creates basic int schema", () => {
    const schema = buildIntSchema({ type: "integer" });
    expect(schema.parse(42)).toBe(42);
  });

  it("rejects non-integers", () => {
    const schema = buildIntSchema({ type: "integer" });
    expect(() => schema.parse(3.14)).toThrow();
  });

  it("enforces positive", () => {
    const schema = buildIntSchema({ type: "integer", positive: true });
    expect(() => schema.parse(0)).toThrow();
    expect(() => schema.parse(-1)).toThrow();
    expect(schema.parse(1)).toBe(1);
  });

  it("enforces min value", () => {
    const schema = buildIntSchema({ type: "integer", min: 10 });
    expect(() => schema.parse(9)).toThrow();
    expect(schema.parse(10)).toBe(10);
  });

  it("enforces max value", () => {
    const schema = buildIntSchema({ type: "integer", max: 100 });
    expect(() => schema.parse(101)).toThrow();
    expect(schema.parse(100)).toBe(100);
  });

  it("applies default value", () => {
    const schema = buildIntSchema({
      type: "integer",
      positive: true,
      default: 5000,
    });
    expect(schema.parse(undefined)).toBe(5000);
  });
});

describe("buildEnumSchema", () => {
  it("creates enum schema from source", () => {
    const schema = buildEnumSchema({
      type: "enum",
      source: "commands.matchTypes",
    });
    expect(schema.parse("exact")).toBe("exact");
    expect(schema.parse("contains")).toBe("contains");
  });

  it("rejects invalid enum value", () => {
    const schema = buildEnumSchema({
      type: "enum",
      source: "commands.matchTypes",
    });
    expect(() => schema.parse("invalid")).toThrow();
  });

  it("throws for missing source", () => {
    expect(() => buildEnumSchema({ type: "enum" })).toThrow(
      "Enum field requires a 'source'",
    );
  });

  it("throws for unknown source", () => {
    expect(() =>
      buildEnumSchema({ type: "enum", source: "unknown.field" }),
    ).toThrow("Unknown source");
  });
});

describe("registry constants", () => {
  it("ENUMS has sortBy and sortOrder", () => {
    expect(ENUMS.sortBy).toContain("name");
    expect(ENUMS.sortBy).toContain("created_at");
    expect(ENUMS.sortOrder).toContain("asc");
    expect(ENUMS.sortOrder).toContain("desc");
  });

  it("SCENARIO_FIELDS has expected keys", () => {
    expect(SCENARIO_FIELDS).toHaveProperty("name");
    expect(SCENARIO_FIELDS).toHaveProperty("steps");
    expect(SCENARIO_FIELDS).toHaveProperty("validations");
    expect(SCENARIO_FIELDS["name"].type).toBe("string");
  });

  it("URL_CHECK_FIELDS has match and value", () => {
    expect(URL_CHECK_FIELDS).toHaveProperty("match");
    expect(URL_CHECK_FIELDS).toHaveProperty("value");
  });

  it("PARAM_CHECK_FIELDS has key, match, value", () => {
    expect(PARAM_CHECK_FIELDS).toHaveProperty("key");
    expect(PARAM_CHECK_FIELDS).toHaveProperty("match");
    expect(PARAM_CHECK_FIELDS).toHaveProperty("value");
  });

  it("PROVIDER_VALUES starts with custom", () => {
    expect(PROVIDER_VALUES[0]).toBe("custom");
    expect(PROVIDER_VALUES.length).toBeGreaterThan(1);
  });

  it("PROVIDERS has entries with urlPatterns", () => {
    const keys = Object.keys(PROVIDERS);
    expect(keys.length).toBeGreaterThan(0);
    for (const key of keys) {
      expect(PROVIDERS[key]).toHaveProperty("urlPatterns");
      expect(PROVIDERS[key]).toHaveProperty("name");
    }
  });
});
