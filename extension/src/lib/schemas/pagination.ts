import { z } from "zod/v4";

// Shared pagination envelope pieces — used by every list response (scenarios, devices, ...).

export const paginationMetaSchema = z.object({
  page: z.number().int(),
  size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export type PaginationMeta = z.infer<typeof paginationMetaSchema>;

export const paginationLinksSchema = z.object({
  self: z.string(),
  first: z.string(),
  last: z.string(),
  next: z.string().nullable(),
  prev: z.string().nullable(),
});

export type PaginationLinks = z.infer<typeof paginationLinksSchema>;
