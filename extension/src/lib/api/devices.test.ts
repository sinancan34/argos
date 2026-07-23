import { describe, it, expect, vi, beforeEach } from "vitest";

const getMock = vi.fn();

vi.mock("./client", () => ({
  api: {
    get: (path: string, opts: { searchParams: URLSearchParams }) =>
      getMock(path, opts),
  },
}));

import { getDevices } from "./devices";

function lastSearchParams(): URLSearchParams {
  const call = getMock.mock.calls.at(-1);
  if (!call) throw new Error("api.get was not called");
  return call[1].searchParams as URLSearchParams;
}

describe("getDevices", () => {
  beforeEach(() => {
    getMock.mockReset();
    getMock.mockReturnValue({
      json: () => Promise.resolve({ data: [], meta: {}, links: {} }),
    });
  });

  it("calls the devices endpoint", async () => {
    await getDevices();
    expect(getMock.mock.calls[0][0]).toBe("devices");
  });

  it("sends status=true", async () => {
    await getDevices({ status: true });
    expect(lastSearchParams().get("status")).toBe("true");
  });

  it("sends status=false (not dropped by a truthiness check)", async () => {
    await getDevices({ status: false });
    expect(lastSearchParams().get("status")).toBe("false");
  });

  it("omits status when undefined", async () => {
    await getDevices({});
    expect(lastSearchParams().has("status")).toBe(false);
  });

  it("serializes name, sort, and paging params", async () => {
    await getDevices({
      name: "pixel",
      sort_by: "name",
      sort_order: "asc",
      page: 2,
      size: 50,
    });
    const p = lastSearchParams();
    expect(p.get("name")).toBe("pixel");
    expect(p.get("sort_by")).toBe("name");
    expect(p.get("sort_order")).toBe("asc");
    expect(p.get("page")).toBe("2");
    expect(p.get("size")).toBe("50");
  });

  it("omits an empty name", async () => {
    await getDevices({ name: "" });
    expect(lastSearchParams().has("name")).toBe(false);
  });
});
