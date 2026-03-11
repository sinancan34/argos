import { z } from "zod/v4";

// --- Enums ---

export const matchTypeValues = [
  "exact",
  "contains",
  "startsWith",
  "endsWith",
  "regex",
  "exists",
] as const;

export const matchTypeSchema = z.enum(matchTypeValues);
export type MatchType = z.infer<typeof matchTypeSchema>;

export const sortByValues = ["name", "created_at", "updated_at"] as const;
export const sortBySchema = z.enum(sortByValues);
export type SortBy = z.infer<typeof sortBySchema>;

export const sortOrderValues = ["asc", "desc"] as const;
export const sortOrderSchema = z.enum(sortOrderValues);
export type SortOrder = z.infer<typeof sortOrderSchema>;

// --- Nested schemas ---

export const paramCheckSchema = z
  .object({
    key: z.string().min(1),
    match: matchTypeSchema,
    value: z.string().optional(),
  })
  .refine(
    (data) => data.match === "exists" || (data.value !== undefined && data.value !== ""),
    { message: "Value is required when match type is not 'exists'" },
  );

export type ParamCheck = z.infer<typeof paramCheckSchema>;

export const stepSchema = z.object({
  id: z.string(),
  command: z.string().min(1),
  params: z.record(z.string(), z.unknown()).default({}),
  timeout: z.number().int().positive().optional(),
});

export type Step = z.infer<typeof stepSchema>;

export const validationSchema = z.object({
  id: z.string(),
  params: z.array(paramCheckSchema).min(1),
});

export type Validation = z.infer<typeof validationSchema>;

// --- Request schemas ---

export const scenarioCreateSchema = z.object({
  name: z.string().min(1).max(500),
  description: z.string().optional(),
  status: z.number().int().default(1),
  step_timeout: z.number().int().positive().default(5000),
  validation_timeout: z.number().int().positive().default(10000),
  steps: z.array(stepSchema).min(1),
  validations: z.array(validationSchema).min(1),
});

export type ScenarioCreate = z.infer<typeof scenarioCreateSchema>;

export const scenarioUpdateSchema = z.object({
  name: z.string().min(1).max(500).optional(),
  description: z.string().optional(),
  status: z.number().int().optional(),
  step_timeout: z.number().int().positive().optional(),
  validation_timeout: z.number().int().positive().optional(),
  steps: z.array(stepSchema).min(1).optional(),
  validations: z.array(validationSchema).min(1).optional(),
});

export type ScenarioUpdate = z.infer<typeof scenarioUpdateSchema>;

// --- Response schemas ---

export const scenarioResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  status: z.number().int(),
  step_timeout: z.number().int(),
  validation_timeout: z.number().int(),
  steps: z.array(z.unknown()),
  validations: z.array(z.unknown()),
  created_at: z.string(),
  updated_at: z.string(),
});

export type ScenarioResponse = z.infer<typeof scenarioResponseSchema>;

export const paginationMetaSchema = z.object({
  page: z.number().int(),
  size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export type PaginationMeta = z.infer<typeof paginationMetaSchema>;

export const singleScenarioEnvelopeSchema = z.object({
  data: scenarioResponseSchema,
});

export type SingleScenarioEnvelope = z.infer<typeof singleScenarioEnvelopeSchema>;

export const scenarioListEnvelopeSchema = z.object({
  data: z.array(scenarioResponseSchema),
  meta: paginationMetaSchema,
});

export type ScenarioListEnvelope = z.infer<typeof scenarioListEnvelopeSchema>;

// --- Query params ---

export interface ScenarioListParams {
  name?: string;
  status?: number;
  sort_by?: SortBy;
  sort_order?: SortOrder;
  page?: number;
  size?: number;
}
