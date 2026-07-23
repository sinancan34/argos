import type { DeviceResponse } from "../schemas/device";

/**
 * Short "393×852 · phone" summary pulled from a device's free-form meta.
 * Any missing piece is dropped, so a device with no viewport/type yields "".
 */
export function deviceSummary(device: DeviceResponse): string {
  const { viewport, type } = device.meta;
  const size =
    viewport?.width && viewport?.height
      ? `${viewport.width}×${viewport.height}`
      : null;
  return [size, type].filter(Boolean).join(" · ");
}
