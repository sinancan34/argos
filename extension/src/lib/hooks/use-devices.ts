import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getDevice, getDevices } from "../api/devices";
import type { DeviceListParams } from "../schemas/device";

export function useDevices(params: DeviceListParams = {}) {
  return useQuery({
    queryKey: ["devices", params],
    queryFn: () => getDevices(params),
    // Keep the previous list visible while a new search request is in flight,
    // so the dropdown doesn't flash empty between keystrokes.
    placeholderData: keepPreviousData,
  });
}

export function useDevice(id: string) {
  return useQuery({
    queryKey: ["devices", "detail", id],
    queryFn: () => getDevice(id),
    enabled: !!id,
  });
}
