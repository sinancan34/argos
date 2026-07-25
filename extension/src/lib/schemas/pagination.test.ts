import { describe, it, expect } from "vitest";
import { paginationMetaSchema, paginationLinksSchema } from "./pagination";

const META = {
  page: 1,
  size: 20,
  total_count: 42,
  total_pages: 3,
};

const LINKS = {
  self: "/api/v1/scenarios?page=1&size=20",
  first: "/api/v1/scenarios?page=1&size=20",
  last: "/api/v1/scenarios?page=3&size=20",
  next: "/api/v1/scenarios?page=2&size=20",
  prev: null,
};

describe("paginationMetaSchema", () => {
  it("parses a populated meta block", () => {
    // Arrange — a typical first-page meta

    // Act
    const parsed = paginationMetaSchema.parse(META);

    // Assert
    expect(parsed).toEqual(META);
  });

  it("parses an empty result set as all zeroes", () => {
    // Arrange
    const emptyMeta = { page: 1, size: 20, total_count: 0, total_pages: 0 };

    // Act
    const parsed = paginationMetaSchema.parse(emptyMeta);

    // Assert
    expect(parsed.total_count).toBe(0);
  });

  it("accepts the maximum page size the backend allows", () => {
    // Arrange — the backend caps size at 100
    const maxSize = 100;

    // Act
    const parsed = paginationMetaSchema.parse({ ...META, size: maxSize });

    // Assert
    expect(parsed.size).toBe(maxSize);
  });

  it("accepts MAX_SAFE_INTEGER as a total_count", () => {
    // Arrange — no upper bound is declared

    // Act
    const parsed = paginationMetaSchema.parse({
      ...META,
      total_count: Number.MAX_SAFE_INTEGER,
    });

    // Assert
    expect(parsed.total_count).toBe(Number.MAX_SAFE_INTEGER);
  });

  it("accepts a negative page because no minimum is declared", () => {
    // Arrange — documents that the schema trusts the backend here

    // Act
    const parsed = paginationMetaSchema.parse({ ...META, page: -1 });

    // Assert
    expect(parsed.page).toBe(-1);
  });

  it("rejects a fractional page", () => {
    // Arrange
    const input = { ...META, page: 1.5 };

    // Act
    const result = paginationMetaSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects NaN as a page", () => {
    // Arrange
    const input = { ...META, page: NaN };

    // Act
    const result = paginationMetaSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects Infinity as a total_pages", () => {
    // Arrange
    const input = { ...META, total_pages: Infinity };

    // Act
    const result = paginationMetaSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a numeric string page (no coercion)", () => {
    // Arrange
    const input = { ...META, page: "1" };

    // Act
    const result = paginationMetaSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a missing total_pages", () => {
    // Arrange
    const { total_pages: _totalPages, ...withoutTotalPages } = META;

    // Act
    const result = paginationMetaSchema.safeParse(withoutTotalPages);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a null size", () => {
    // Arrange
    const input = { ...META, size: null };

    // Act
    const result = paginationMetaSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects an empty object", () => {
    // Arrange — every field is required

    // Act
    const result = paginationMetaSchema.safeParse({});

    // Assert
    expect(result.success).toBe(false);
  });

  it("strips unknown keys", () => {
    // Arrange
    const input = { ...META, cursor: "abc" };

    // Act
    const parsed = paginationMetaSchema.parse(input);

    // Assert
    expect(parsed).not.toHaveProperty("cursor");
  });
});

describe("paginationLinksSchema", () => {
  it("parses a middle-page link block", () => {
    // Arrange — next present, prev null

    // Act
    const parsed = paginationLinksSchema.parse(LINKS);

    // Assert
    expect(parsed).toEqual(LINKS);
  });

  it("accepts a null next on the last page", () => {
    // Arrange
    const input = { ...LINKS, next: null };

    // Act
    const parsed = paginationLinksSchema.parse(input);

    // Assert
    expect(parsed.next).toBeNull();
  });

  it("accepts both next and prev being null on a single-page result", () => {
    // Arrange
    const input = { ...LINKS, next: null, prev: null };

    // Act
    const parsed = paginationLinksSchema.parse(input);

    // Assert
    expect(parsed.prev).toBeNull();
  });

  it("accepts a non-null prev", () => {
    // Arrange
    const prevLink = "/api/v1/scenarios?page=1&size=20";

    // Act
    const parsed = paginationLinksSchema.parse({ ...LINKS, prev: prevLink });

    // Assert
    expect(parsed.prev).toBe(prevLink);
  });

  it("accepts an empty string self link because no format is enforced", () => {
    // Arrange — documents that links are plain strings, not validated URLs

    // Act
    const parsed = paginationLinksSchema.parse({ ...LINKS, self: "" });

    // Assert
    expect(parsed.self).toBe("");
  });

  it("rejects an undefined next (null is required, not absent)", () => {
    // Arrange
    const { next: _next, ...withoutNext } = LINKS;

    // Act
    const result = paginationLinksSchema.safeParse(withoutNext);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a missing self link", () => {
    // Arrange
    const { self: _self, ...withoutSelf } = LINKS;

    // Act
    const result = paginationLinksSchema.safeParse(withoutSelf);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects a numeric last link", () => {
    // Arrange
    const input = { ...LINKS, last: 3 };

    // Act
    const result = paginationLinksSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects null for a non-nullable link", () => {
    // Arrange — only next and prev are nullable
    const input = { ...LINKS, first: null };

    // Act
    const result = paginationLinksSchema.safeParse(input);

    // Assert
    expect(result.success).toBe(false);
  });

  it("rejects an empty object", () => {
    // Arrange — every link key is required

    // Act
    const result = paginationLinksSchema.safeParse({});

    // Assert
    expect(result.success).toBe(false);
  });
});
