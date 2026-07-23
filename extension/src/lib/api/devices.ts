import { api } from "./client";
import type {
  DeviceListEnvelope,
  DeviceListParams,
  SingleDeviceEnvelope,
} from "../schemas/device";

export async function getDevices(
  params: DeviceListParams = {},
): Promise<DeviceListEnvelope> {
  const searchParams = new URLSearchParams();

  if (params.name) searchParams.set("name", params.name);
  // status is a boolean — guard on `undefined` (not truthiness) so `false` is still sent.
  if (params.status !== undefined) searchParams.set("status", String(params.status));
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.sort_order) searchParams.set("sort_order", params.sort_order);
  if (params.page) searchParams.set("page", String(params.page));
  if (params.size) searchParams.set("size", String(params.size));

  return api.get("devices", { searchParams }).json<DeviceListEnvelope>();
}

export async function getDevice(id: string): Promise<SingleDeviceEnvelope> {
  return api.get(`devices/${id}`).json<SingleDeviceEnvelope>();
}
