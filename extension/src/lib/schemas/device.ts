import { z } from "zod/v4";
import { paginationMetaSchema, paginationLinksSchema } from "./pagination";
import type { SortBy, SortOrder } from "./scenario";

// --- Meta (free-form on the backend; kept relaxed so unexpected keys never break parsing) ---

const deviceViewportSchema = z
  .object({
    width: z.number().optional(),
    height: z.number().optional(),
    device_pixel_ratio: z.number().optional(),
  })
  .loose();

const deviceCapabilitiesSchema = z
  .object({
    touch: z.boolean().optional(),
    mobile: z.boolean().optional(),
  })
  .loose();

export const deviceMetaSchema = z
  .object({
    source: z.string().optional(),
    type: z.string().optional(),
    user_agent: z.string().optional(),
    viewport: deviceViewportSchema.optional(),
    capabilities: deviceCapabilitiesSchema.optional(),
    platform: z.string().nullable().optional(),
    platform_version: z.string().nullable().optional(),
  })
  .loose();

export type DeviceMeta = z.infer<typeof deviceMetaSchema>;

// --- Response schemas ---

export const deviceResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  meta: deviceMetaSchema,
  status: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type DeviceResponse = z.infer<typeof deviceResponseSchema>;

export const singleDeviceEnvelopeSchema = z.object({
  data: deviceResponseSchema,
});

export type SingleDeviceEnvelope = z.infer<typeof singleDeviceEnvelopeSchema>;

export const deviceListEnvelopeSchema = z.object({
  data: z.array(deviceResponseSchema),
  meta: paginationMetaSchema,
  links: paginationLinksSchema,
});

export type DeviceListEnvelope = z.infer<typeof deviceListEnvelopeSchema>;

// --- Query params ---

export interface DeviceListParams {
  name?: string;
  status?: boolean;
  sort_by?: SortBy;
  sort_order?: SortOrder;
  page?: number;
  size?: number;
}
