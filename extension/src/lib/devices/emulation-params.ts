import type { DeviceMeta } from "../schemas/device";

// CDP Emulation params distilled from a device's free-form meta. Kept as a plain
// data shape (no chrome APIs) so it can be built and unit-tested in isolation,
// then handed to the background applier that talks to chrome.debugger.

export interface EmulationDeviceMetrics {
  width: number;
  height: number;
  deviceScaleFactor: number;
  mobile: boolean;
}

export interface EmulationTouch {
  enabled: boolean;
  maxTouchPoints: number;
}

export interface EmulationParams {
  deviceMetrics: EmulationDeviceMetrics;
  userAgent?: string;
  touch: EmulationTouch;
}

/**
 * Translate a device's `meta` into CDP Emulation params, or `null` when the
 * device carries no usable viewport (width + height). Callers treat `null` as
 * "run without emulation" rather than an error, since `meta` is free-form and
 * every field is optional. Missing pieces fall back to non-emulating defaults
 * (DPR 1, not mobile, no touch, no UA override).
 */
export function buildEmulationParams(meta: DeviceMeta): EmulationParams | null {
  const width = meta.viewport?.width;
  const height = meta.viewport?.height;

  if (typeof width !== "number" || typeof height !== "number") {
    return null;
  }

  const touchEnabled = meta.capabilities?.touch === true;

  return {
    deviceMetrics: {
      width,
      height,
      deviceScaleFactor: meta.viewport?.device_pixel_ratio ?? 1,
      mobile: meta.capabilities?.mobile === true,
    },
    userAgent: meta.user_agent || undefined,
    touch: {
      enabled: touchEnabled,
      maxTouchPoints: touchEnabled ? 1 : 0,
    },
  };
}
