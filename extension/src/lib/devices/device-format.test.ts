import { describe, it, expect } from "vitest";
import { deviceSummary } from "./device-format";
import type { DeviceResponse } from "../schemas/device";

function device(meta: DeviceResponse["meta"]): DeviceResponse {
  return {
    id: "id",
    name: "Test",
    meta,
    status: true,
    created_at: "",
    updated_at: "",
  };
}

describe("deviceSummary", () => {
  it("combines resolution and type", () => {
    expect(
      deviceSummary(
        device({ type: "phone", viewport: { width: 393, height: 852 } }),
      ),
    ).toBe("393×852 · phone");
  });

  it("drops resolution when viewport is incomplete", () => {
    expect(deviceSummary(device({ type: "tablet", viewport: { width: 768 } }))).toBe(
      "tablet",
    );
  });

  it("drops type when absent", () => {
    expect(
      deviceSummary(device({ viewport: { width: 1024, height: 1366 } })),
    ).toBe("1024×1366");
  });

  it("returns an empty string when meta has neither", () => {
    expect(deviceSummary(device({}))).toBe("");
  });
});
