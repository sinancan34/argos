import { describe, it, expect } from "vitest";
import { buildEmulationParams } from "./emulation-params";
import type { DeviceMeta } from "../schemas/device";

describe("buildEmulationParams", () => {
  it("maps a full phone meta to CDP emulation params", () => {
    const meta: DeviceMeta = {
      type: "phone",
      user_agent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5) Safari/604.1",
      viewport: { width: 375, height: 667, device_pixel_ratio: 2 },
      capabilities: { touch: true, mobile: true },
    };

    expect(buildEmulationParams(meta)).toEqual({
      deviceMetrics: {
        width: 375,
        height: 667,
        deviceScaleFactor: 2,
        mobile: true,
      },
      userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5) Safari/604.1",
      touch: { enabled: true, maxTouchPoints: 1 },
    });
  });

  it("maps a tablet meta", () => {
    const meta: DeviceMeta = {
      type: "tablet",
      user_agent: "iPad UA",
      viewport: { width: 768, height: 1024, device_pixel_ratio: 2 },
      capabilities: { touch: true, mobile: false },
    };

    const params = buildEmulationParams(meta);
    expect(params?.deviceMetrics).toEqual({
      width: 768,
      height: 1024,
      deviceScaleFactor: 2,
      mobile: false,
    });
    expect(params?.touch).toEqual({ enabled: true, maxTouchPoints: 1 });
  });

  it("returns null when the viewport is absent", () => {
    expect(buildEmulationParams({ type: "phone" })).toBeNull();
  });

  it("returns null when width or height is missing", () => {
    expect(buildEmulationParams({ viewport: { width: 375 } })).toBeNull();
    expect(buildEmulationParams({ viewport: { height: 667 } })).toBeNull();
  });

  it("defaults deviceScaleFactor to 1 when device_pixel_ratio is missing", () => {
    const params = buildEmulationParams({
      viewport: { width: 1280, height: 800 },
    });
    expect(params?.deviceMetrics.deviceScaleFactor).toBe(1);
  });

  it("defaults mobile to false and disables touch when capabilities are missing", () => {
    const params = buildEmulationParams({
      viewport: { width: 1280, height: 800, device_pixel_ratio: 1 },
    });
    expect(params?.deviceMetrics.mobile).toBe(false);
    expect(params?.touch).toEqual({ enabled: false, maxTouchPoints: 0 });
  });

  it("omits the user agent override when user_agent is absent or empty", () => {
    expect(
      buildEmulationParams({ viewport: { width: 375, height: 667 } })?.userAgent,
    ).toBeUndefined();
    expect(
      buildEmulationParams({
        user_agent: "",
        viewport: { width: 375, height: 667 },
      })?.userAgent,
    ).toBeUndefined();
  });

  it("treats explicit false capabilities as non-mobile, no touch", () => {
    const params = buildEmulationParams({
      viewport: { width: 1920, height: 1080, device_pixel_ratio: 1 },
      capabilities: { touch: false, mobile: false },
    });
    expect(params?.deviceMetrics.mobile).toBe(false);
    expect(params?.touch.enabled).toBe(false);
  });
});
