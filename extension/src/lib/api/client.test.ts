import { describe, it, expect, vi, beforeEach } from "vitest";

interface ApiErrorEnvelope {
  error: { code: string; message: string; details: unknown[] };
}

type KyErrorLike = Error & { response?: Response };
type BeforeErrorHook = (error: KyErrorLike) => Promise<KyErrorLike>;

interface KyConfig {
  prefixUrl: string;
  hooks: { beforeError: BeforeErrorHook[] };
}

// client.ts calls ky.create at module-eval time, so these mocks must exist before
// the module graph loads — vi.hoisted runs ahead of the hoisted imports.
const { KY_INSTANCE, createMock, parseApiErrorMock } = vi.hoisted(() => {
  const instance = { marker: "ky-instance" };
  return {
    KY_INSTANCE: instance,
    createMock: vi.fn(() => instance),
    parseApiErrorMock: vi.fn(),
  };
});

vi.mock("ky", () => ({
  default: { create: (config: KyConfig) => createMock(config) },
}));

vi.mock("./errors", () => ({
  parseApiError: (response: Response) => parseApiErrorMock(response),
}));

import { api } from "./client";

const ORIGINAL_MESSAGE = "Request failed with status code 422";
const BACKEND_MESSAGE = "Validation failed for 1 field";

/** The config object client.ts handed to ky.create at module load. */
function kyConfig(): KyConfig {
  const call = createMock.mock.calls[0];
  if (!call) throw new Error("ky.create was not called");
  return call[0] as unknown as KyConfig;
}

function beforeErrorHook(): BeforeErrorHook {
  return kyConfig().hooks.beforeError[0];
}

function makeApiErrorEnvelope(): ApiErrorEnvelope {
  return {
    error: {
      code: "VALIDATION_ERROR",
      message: BACKEND_MESSAGE,
      details: [],
    },
  };
}

function makeKyError(withResponse: boolean): KyErrorLike {
  const error: KyErrorLike = new Error(ORIGINAL_MESSAGE);
  if (withResponse) {
    error.response = new Response("{}", { status: 422 });
  }
  return error;
}

describe("api client construction", () => {
  it("exports the instance returned by ky.create", () => {
    // Arrange — the module was created at import time

    // Act
    const instance = api;

    // Assert
    expect(instance).toBe(KY_INSTANCE);
  });

  it("calls ky.create exactly once", () => {
    // Arrange — module-level side effect

    // Act
    const callCount = createMock.mock.calls.length;

    // Assert
    expect(callCount).toBe(1);
  });

  it("points the prefixUrl at the versioned API path", () => {
    // Arrange — built from VITE_API_BASE_URL at build time

    // Act
    const { prefixUrl } = kyConfig();

    // Assert
    expect(prefixUrl.endsWith("/api/v1")).toBe(true);
  });

  it("registers exactly one beforeError hook", () => {
    // Arrange — the envelope parser is the only hook

    // Act
    const hooks = kyConfig().hooks.beforeError;

    // Assert
    expect(hooks).toHaveLength(1);
  });
});

describe("beforeError hook", () => {
  beforeEach(() => {
    parseApiErrorMock.mockReset();
  });

  it("returns the same error instance it was given", async () => {
    // Arrange
    parseApiErrorMock.mockResolvedValue(null);
    const error = makeKyError(true);

    // Act
    const result = await beforeErrorHook()(error);

    // Assert
    expect(result).toBe(error);
  });

  it("passes the response to parseApiError", async () => {
    // Arrange
    parseApiErrorMock.mockResolvedValue(null);
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(parseApiErrorMock).toHaveBeenCalledWith(error.response);
  });

  it("calls parseApiError exactly once when a response is present", async () => {
    // Arrange
    parseApiErrorMock.mockResolvedValue(null);

    // Act
    await beforeErrorHook()(makeKyError(true));

    // Assert
    expect(parseApiErrorMock).toHaveBeenCalledTimes(1);
  });

  it("skips parseApiError when the error carries no response", async () => {
    // Arrange — network-level failures have no response

    // Act
    await beforeErrorHook()(makeKyError(false));

    // Assert
    expect(parseApiErrorMock).not.toHaveBeenCalled();
  });

  it("leaves the message untouched when there is no response", async () => {
    // Arrange
    const error = makeKyError(false);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error.message).toBe(ORIGINAL_MESSAGE);
  });

  it("attaches no apiError property when there is no response", async () => {
    // Arrange
    const error = makeKyError(false);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error).not.toHaveProperty("apiError");
  });

  it("replaces the message with the backend message on a parsed envelope", async () => {
    // Arrange
    parseApiErrorMock.mockResolvedValue(makeApiErrorEnvelope());
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error.message).toBe(BACKEND_MESSAGE);
  });

  it("attaches the parsed envelope as apiError", async () => {
    // Arrange
    const envelope = makeApiErrorEnvelope();
    parseApiErrorMock.mockResolvedValue(envelope);
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect((error as unknown as Record<string, unknown>).apiError).toBe(
      envelope,
    );
  });

  it("leaves the message untouched when the envelope cannot be parsed", async () => {
    // Arrange
    parseApiErrorMock.mockResolvedValue(null);
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error.message).toBe(ORIGINAL_MESSAGE);
  });

  it("attaches no apiError property when the envelope cannot be parsed", async () => {
    // Arrange
    parseApiErrorMock.mockResolvedValue(null);
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error).not.toHaveProperty("apiError");
  });

  it("writes an empty backend message through to the error", async () => {
    // Arrange — the hook does not guard against an empty message
    parseApiErrorMock.mockResolvedValue({
      error: { code: "UNKNOWN", message: "", details: [] },
    });
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error.message).toBe("");
  });

  it("preserves a Turkish backend message", async () => {
    // Arrange
    const turkishMessage = "Doğrulama başarısız oldu";
    parseApiErrorMock.mockResolvedValue({
      error: { code: "VALIDATION_ERROR", message: turkishMessage, details: [] },
    });
    const error = makeKyError(true);

    // Act
    await beforeErrorHook()(error);

    // Assert
    expect(error.message).toBe(turkishMessage);
  });

  it("propagates a rejection from parseApiError", async () => {
    // Arrange
    parseApiErrorMock.mockRejectedValue(new Error("parse blew up"));

    // Act & Assert
    await expect(beforeErrorHook()(makeKyError(true))).rejects.toThrow(
      "parse blew up",
    );
  });
});
