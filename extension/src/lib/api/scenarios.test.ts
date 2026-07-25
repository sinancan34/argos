import { describe, it, expect, vi, beforeEach } from "vitest";

const getMock = vi.fn();
const postMock = vi.fn();
const patchMock = vi.fn();
const deleteMock = vi.fn();

vi.mock("./client", () => ({
  api: {
    get: (path: string, opts?: { searchParams: URLSearchParams }) =>
      getMock(path, opts),
    post: (path: string, opts?: { json: unknown }) => postMock(path, opts),
    patch: (path: string, opts?: { json: unknown }) => patchMock(path, opts),
    delete: (path: string, opts?: { json: unknown }) => deleteMock(path, opts),
  },
}));

import {
  getScenarios,
  getScenario,
  createScenario,
  updateScenario,
  deleteScenario,
} from "./scenarios";
import type { ScenarioCreate, ScenarioUpdate } from "../schemas/scenario";

const SCENARIO_ID = "9c1e4b7a-0000-4000-8000-000000000001";
const DEVICE_ID = "5b1f0d2e-0000-4000-8000-000000000000";
const PAGE = 2;
const SIZE = 50;
const STEP_TIMEOUT = 5000;
const VALIDATION_TIMEOUT = 10000;
const LONG_NAME_LENGTH = 10000;

/** Reads the searchParams passed to the most recent api.get call. */
function lastSearchParams(): URLSearchParams {
  const call = getMock.mock.calls.at(-1);
  if (!call) throw new Error("api.get was not called");
  return call[1].searchParams as URLSearchParams;
}

/** Reads the path passed to the most recent call of the given mock. */
function lastPath(mock: typeof getMock): string {
  const call = mock.mock.calls.at(-1);
  if (!call) throw new Error("mock was not called");
  return call[0] as string;
}

/** Reads the json body passed to the most recent call of the given mock. */
function lastJson(mock: typeof postMock): unknown {
  const call = mock.mock.calls.at(-1);
  if (!call) throw new Error("mock was not called");
  return call[1].json;
}

function makeScenarioCreate(
  overrides: Partial<ScenarioCreate> = {},
): ScenarioCreate {
  return {
    name: "Checkout flow",
    status: true,
    device_id: DEVICE_ID,
    step_timeout: STEP_TIMEOUT,
    validation_timeout: VALIDATION_TIMEOUT,
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

describe("getScenarios", () => {
  beforeEach(() => {
    getMock.mockReset();
    getMock.mockReturnValue({
      json: () => Promise.resolve({ data: [], meta: {}, links: {} }),
    });
  });

  it("calls the scenarios endpoint", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios();

    // Assert
    expect(lastPath(getMock)).toBe("scenarios");
  });

  it("returns the parsed list envelope", async () => {
    // Arrange
    const envelope = {
      data: [],
      meta: { page: 1, size: 20, total_count: 0, total_pages: 0 },
      links: { self: "/x", first: "/x", last: "/x", next: null, prev: null },
    };
    getMock.mockReturnValue({ json: () => Promise.resolve(envelope) });

    // Act
    const result = await getScenarios();

    // Assert
    expect(result).toEqual(envelope);
  });

  it("sends no query params when called with no arguments", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios();

    // Assert
    expect(lastSearchParams().toString()).toBe("");
  });

  it("sends status=true", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios({ status: true });

    // Assert
    expect(lastSearchParams().get("status")).toBe("true");
  });

  it("sends status=false (not dropped by a truthiness check)", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios({ status: false });

    // Assert
    expect(lastSearchParams().get("status")).toBe("false");
  });

  it("omits status when undefined", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios({ status: undefined });

    // Assert
    expect(lastSearchParams().has("status")).toBe(false);
  });

  it("serializes name, sort, and paging params together", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios({
      name: "checkout",
      sort_by: "created_at",
      sort_order: "desc",
      page: PAGE,
      size: SIZE,
    });

    // Assert
    expect(lastSearchParams().toString()).toBe(
      `name=checkout&sort_by=created_at&sort_order=desc&page=${PAGE}&size=${SIZE}`,
    );
  });

  it("omits an empty name", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenarios({ name: "" });

    // Assert
    expect(lastSearchParams().has("name")).toBe(false);
  });

  it("sends a whitespace-only name verbatim", async () => {
    // Arrange
    const whitespaceName = " \t\n ";

    // Act
    await getScenarios({ name: whitespaceName });

    // Assert
    expect(lastSearchParams().get("name")).toBe(whitespaceName);
  });

  it("sends a Turkish name without mangling it", async () => {
    // Arrange
    const turkishName = "ödeme akışı ğüşöçıİ";

    // Act
    await getScenarios({ name: turkishName });

    // Assert
    expect(lastSearchParams().get("name")).toBe(turkishName);
  });

  it("sends an emoji name without mangling it", async () => {
    // Arrange
    const emojiName = "checkout 🛒✅";

    // Act
    await getScenarios({ name: emojiName });

    // Assert
    expect(lastSearchParams().get("name")).toBe(emojiName);
  });

  it("sends a very long name in full", async () => {
    // Arrange
    const longName = "a".repeat(LONG_NAME_LENGTH);

    // Act
    await getScenarios({ name: longName });

    // Assert
    expect(lastSearchParams().get("name")).toHaveLength(LONG_NAME_LENGTH);
  });

  it("omits page 0 because the guard is a truthiness check", async () => {
    // Arrange — page 0 is falsy, so the current implementation drops it

    // Act
    await getScenarios({ page: 0 });

    // Assert
    expect(lastSearchParams().has("page")).toBe(false);
  });

  it("omits size 0 because the guard is a truthiness check", async () => {
    // Arrange — size 0 is falsy, so the current implementation drops it

    // Act
    await getScenarios({ size: 0 });

    // Assert
    expect(lastSearchParams().has("size")).toBe(false);
  });

  it("serializes a negative page number", async () => {
    // Arrange
    const negativePage = -1;

    // Act
    await getScenarios({ page: negativePage });

    // Assert
    expect(lastSearchParams().get("page")).toBe("-1");
  });

  it("serializes MAX_SAFE_INTEGER as a page number", async () => {
    // Arrange — boundary of the safe integer range

    // Act
    await getScenarios({ page: Number.MAX_SAFE_INTEGER });

    // Assert
    expect(lastSearchParams().get("page")).toBe(
      String(Number.MAX_SAFE_INTEGER),
    );
  });

  it("serializes Infinity as a page number", async () => {
    // Arrange — Infinity is truthy so it passes the guard

    // Act
    await getScenarios({ page: Infinity });

    // Assert
    expect(lastSearchParams().get("page")).toBe("Infinity");
  });

  it("omits NaN as a page number because NaN is falsy", async () => {
    // Arrange — NaN is falsy, so the guard drops it

    // Act
    await getScenarios({ page: NaN });

    // Assert
    expect(lastSearchParams().has("page")).toBe(false);
  });

  it("propagates a rejection from the client", async () => {
    // Arrange
    getMock.mockReturnValue({
      json: () => Promise.reject(new Error("Network error")),
    });

    // Act & Assert
    await expect(getScenarios()).rejects.toThrow("Network error");
  });
});

describe("getScenario", () => {
  beforeEach(() => {
    getMock.mockReset();
    getMock.mockReturnValue({ json: () => Promise.resolve({ data: {} }) });
  });

  it("requests the scenario by id", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenario(SCENARIO_ID);

    // Assert
    expect(lastPath(getMock)).toBe(`scenarios/${SCENARIO_ID}`);
  });

  it("calls the client exactly once", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenario(SCENARIO_ID);

    // Assert
    expect(getMock).toHaveBeenCalledTimes(1);
  });

  it("passes no request options", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await getScenario(SCENARIO_ID);

    // Assert
    expect(getMock.mock.calls[0][1]).toBeUndefined();
  });

  it("returns the parsed single envelope", async () => {
    // Arrange
    const envelope = { data: { id: SCENARIO_ID } };
    getMock.mockReturnValue({ json: () => Promise.resolve(envelope) });

    // Act
    const result = await getScenario(SCENARIO_ID);

    // Assert
    expect(result).toEqual(envelope);
  });

  it("builds a path with a trailing slash for an empty id", async () => {
    // Arrange — documents that the id is not validated before use

    // Act
    await getScenario("");

    // Assert
    expect(lastPath(getMock)).toBe("scenarios/");
  });

  it("interpolates an id containing a slash without escaping it", async () => {
    // Arrange — documents that ids are not URL-encoded
    const idWithSlash = "a/b";

    // Act
    await getScenario(idWithSlash);

    // Assert
    expect(lastPath(getMock)).toBe("scenarios/a/b");
  });

  it("propagates a rejection from the client", async () => {
    // Arrange
    getMock.mockReturnValue({
      json: () => Promise.reject(new Error("Not found")),
    });

    // Act & Assert
    await expect(getScenario(SCENARIO_ID)).rejects.toThrow("Not found");
  });
});

describe("createScenario", () => {
  beforeEach(() => {
    postMock.mockReset();
    postMock.mockReturnValue({ json: () => Promise.resolve({ data: {} }) });
  });

  it("posts to the scenarios collection", async () => {
    // Arrange
    const payload = makeScenarioCreate();

    // Act
    await createScenario(payload);

    // Assert
    expect(lastPath(postMock)).toBe("scenarios");
  });

  it("sends the payload as the json body", async () => {
    // Arrange
    const payload = makeScenarioCreate();

    // Act
    await createScenario(payload);

    // Assert
    expect(lastJson(postMock)).toEqual(payload);
  });

  it("does not mutate the payload it is given", async () => {
    // Arrange
    const payload = makeScenarioCreate();
    const snapshot = structuredClone(payload);

    // Act
    await createScenario(payload);

    // Assert
    expect(payload).toEqual(snapshot);
  });

  it("returns the parsed single envelope", async () => {
    // Arrange
    const envelope = { data: { id: SCENARIO_ID } };
    postMock.mockReturnValue({ json: () => Promise.resolve(envelope) });

    // Act
    const result = await createScenario(makeScenarioCreate());

    // Assert
    expect(result).toEqual(envelope);
  });

  it("propagates a rejection from the client", async () => {
    // Arrange
    postMock.mockReturnValue({
      json: () => Promise.reject(new Error("Validation failed")),
    });

    // Act & Assert
    await expect(createScenario(makeScenarioCreate())).rejects.toThrow(
      "Validation failed",
    );
  });
});

describe("updateScenario", () => {
  beforeEach(() => {
    patchMock.mockReset();
    patchMock.mockReturnValue({ json: () => Promise.resolve({ data: {} }) });
  });

  it("patches the scenario by id", async () => {
    // Arrange
    const patch: ScenarioUpdate = { name: "Renamed" };

    // Act
    await updateScenario(SCENARIO_ID, patch);

    // Assert
    expect(lastPath(patchMock)).toBe(`scenarios/${SCENARIO_ID}`);
  });

  it("sends the patch as the json body", async () => {
    // Arrange
    const patch: ScenarioUpdate = { name: "Renamed" };

    // Act
    await updateScenario(SCENARIO_ID, patch);

    // Assert
    expect(lastJson(patchMock)).toEqual(patch);
  });

  it("sends an empty patch body unchanged", async () => {
    // Arrange
    const patch: ScenarioUpdate = {};

    // Act
    await updateScenario(SCENARIO_ID, patch);

    // Assert
    expect(lastJson(patchMock)).toEqual({});
  });

  it("sends status=false in the body rather than dropping it", async () => {
    // Arrange
    const patch: ScenarioUpdate = { status: false };

    // Act
    await updateScenario(SCENARIO_ID, patch);

    // Assert
    expect(lastJson(patchMock)).toEqual({ status: false });
  });

  it("returns the parsed single envelope", async () => {
    // Arrange
    const envelope = { data: { id: SCENARIO_ID } };
    patchMock.mockReturnValue({ json: () => Promise.resolve(envelope) });

    // Act
    const result = await updateScenario(SCENARIO_ID, {});

    // Assert
    expect(result).toEqual(envelope);
  });

  it("propagates a rejection from the client", async () => {
    // Arrange
    patchMock.mockReturnValue({
      json: () => Promise.reject(new Error("Conflict")),
    });

    // Act & Assert
    await expect(updateScenario(SCENARIO_ID, {})).rejects.toThrow("Conflict");
  });
});

describe("deleteScenario", () => {
  beforeEach(() => {
    deleteMock.mockReset();
    deleteMock.mockReturnValue({
      json: () => Promise.resolve({ data: { id: SCENARIO_ID } }),
    });
  });

  it("deletes the scenario by id", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await deleteScenario(SCENARIO_ID);

    // Assert
    expect(lastPath(deleteMock)).toBe(`scenarios/${SCENARIO_ID}`);
  });

  it("calls the client exactly once", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await deleteScenario(SCENARIO_ID);

    // Assert
    expect(deleteMock).toHaveBeenCalledTimes(1);
  });

  it("returns the delete envelope carrying the id", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    const result = await deleteScenario(SCENARIO_ID);

    // Assert
    expect(result).toEqual({ data: { id: SCENARIO_ID } });
  });

  it("propagates a rejection from the client", async () => {
    // Arrange
    deleteMock.mockReturnValue({
      json: () => Promise.reject(new Error("Forbidden")),
    });

    // Act & Assert
    await expect(deleteScenario(SCENARIO_ID)).rejects.toThrow("Forbidden");
  });
});
