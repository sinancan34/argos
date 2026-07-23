import { describe, it, expect } from "vitest";
import { deviceResponseSchema } from "./device";

const seededRow = {
  id: "5b1f0d2e-0000-4000-8000-000000000000",
  name: "iPhone SE",
  meta: {
    source: "chrome-devtools",
    type: "phone",
    user_agent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X)",
    viewport: { width: 375, height: 667, device_pixel_ratio: 2 },
    capabilities: { touch: true, mobile: true },
    platform: "iOS",
    platform_version: "18.5",
  },
  status: true,
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
};

describe("deviceResponseSchema", () => {
  it("parses a seeded device row including nested viewport", () => {
    const parsed = deviceResponseSchema.parse(seededRow);
    expect(parsed.name).toBe("iPhone SE");
    expect(parsed.status).toBe(true);
    expect(parsed.meta.viewport?.width).toBe(375);
    expect(parsed.meta.viewport?.device_pixel_ratio).toBe(2);
    expect(parsed.meta.capabilities?.touch).toBe(true);
  });

  it("tolerates an empty meta object", () => {
    const parsed = deviceResponseSchema.parse({ ...seededRow, meta: {} });
    expect(parsed.meta.type).toBeUndefined();
    expect(parsed.meta.viewport).toBeUndefined();
  });

  it("preserves unexpected meta keys (loose)", () => {
    const parsed = deviceResponseSchema.parse({
      ...seededRow,
      meta: { ...seededRow.meta, orientation: "portrait" },
    });
    expect((parsed.meta as Record<string, unknown>).orientation).toBe(
      "portrait",
    );
  });

  it("accepts a null platform", () => {
    const parsed = deviceResponseSchema.parse({
      ...seededRow,
      meta: { ...seededRow.meta, platform: null, platform_version: null },
    });
    expect(parsed.meta.platform).toBeNull();
  });

  it("rejects a non-boolean status", () => {
    expect(() =>
      deviceResponseSchema.parse({ ...seededRow, status: "true" }),
    ).toThrow();
  });

  it("rejects a missing required field", () => {
    const { name: _name, ...withoutName } = seededRow;
    expect(() => deviceResponseSchema.parse(withoutName)).toThrow();
  });
});
