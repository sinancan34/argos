import { describe, it, expect } from "vitest";
import { parseApiError } from "./errors";

function mockResponse(body: unknown, ok = false): Response {
  return {
    ok,
    status: ok ? 200 : 400,
    clone() {
      return this;
    },
    json() {
      return Promise.resolve(body);
    },
  } as unknown as Response;
}

describe("parseApiError", () => {
  it("parses valid API error response", async () => {
    const body = {
      error: {
        code: "NOT_FOUND",
        message: "Scenario not found",
        details: [],
      },
    };
    const result = await parseApiError(mockResponse(body));
    expect(result).toEqual(body);
  });

  it("returns null for non-error response body", async () => {
    const body = { data: { id: "123" } };
    const result = await parseApiError(mockResponse(body));
    expect(result).toBeNull();
  });

  it("returns null when body is not an object", async () => {
    const result = await parseApiError(mockResponse("not json"));
    expect(result).toBeNull();
  });

  it("returns null when json parsing fails", async () => {
    const response = {
      clone() {
        return this;
      },
      json() {
        return Promise.reject(new Error("parse error"));
      },
    } as unknown as Response;
    const result = await parseApiError(response);
    expect(result).toBeNull();
  });

  it("returns null when error.code is not a string", async () => {
    const body = { error: { code: 123, message: "bad" } };
    const result = await parseApiError(mockResponse(body));
    expect(result).toBeNull();
  });

  it("returns null for null body", async () => {
    const result = await parseApiError(mockResponse(null));
    expect(result).toBeNull();
  });
});
