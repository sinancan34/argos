import { z } from "zod/v4";
import commandDefs from "../../../../shared/commands.json";
import { commandValues } from "../commands";
import {
  ENUMS,
  SCENARIO_FIELDS,
  PARAM_CHECK_FIELDS,
  URL_CHECK_FIELDS,
  PROVIDER_VALUES,
  buildStringSchema,
  buildIntSchema,
  buildEnumSchema,
} from "../validation-registry";

// --- Enums (sourced from shared sources) ---

export const matchTypeValues = commandDefs.matchTypes as [string, ...string[]];

const matchTypeSchema = z.enum(matchTypeValues);

const sortByValues = ENUMS.sortBy as [string, ...string[]];
const sortBySchema = z.enum(sortByValues);
export type SortBy = z.infer<typeof sortBySchema>;

const sortOrderValues = ENUMS.sortOrder as [string, ...string[]];
const sortOrderSchema = z.enum(sortOrderValues);
export type SortOrder = z.infer<typeof sortOrderSchema>;

// --- Nested schemas ---

const _pcKeySch = buildStringSchema(PARAM_CHECK_FIELDS["key"]);
const _pcMatchSch = buildEnumSchema(PARAM_CHECK_FIELDS["match"]);
const _pcCond = PARAM_CHECK_FIELDS["value"].conditionalRequired!;

const paramCheckSchema = z
  .object({
    key: _pcKeySch,
    match: _pcMatchSch,
    value: z.string().optional(),
  })
  .refine(
    (data) =>
      data.match === _pcCond.unless.equals ||
      (data.value !== undefined && data.value.length >= _pcCond.minLength),
    { message: "Value is required when match type is not 'exists'" },
  );


const _ucMatchSch = buildEnumSchema(URL_CHECK_FIELDS["match"]);
const _ucCond = URL_CHECK_FIELDS["value"].conditionalRequired!;

const urlCheckSchema = z
  .object({
    match: _ucMatchSch,
    value: z.string().optional(),
  })
  .refine(
    (data) =>
      data.match === _ucCond.unless.equals ||
      (data.value !== undefined && data.value.length >= _ucCond.minLength),
    { message: "Value is required when match type is not 'exists'" },
  );


const stepSchema = z.object({
  id: z.string(),
  command: z.enum(commandValues),
  params: z.record(z.string(), z.unknown()).default({}),
});

export type Step = z.infer<typeof stepSchema>;

export const providerValues = PROVIDER_VALUES;

const validationSchema = z
  .object({
    id: z.string(),
    provider: z.enum(PROVIDER_VALUES).default("custom"),
    url: urlCheckSchema.optional(),
    params: z.array(paramCheckSchema).default([]),
  })
  .refine(
    (data) => data.provider !== "custom" || data.url !== undefined,
    { message: "URL check is required when provider is 'Custom URL'" },
  );

export type Validation = z.infer<typeof validationSchema>;

// --- Request schemas ---

export const scenarioStatusValues = (SCENARIO_FIELDS["status"].values ?? ["active", "inactive"]) as [string, ...string[]];
export type ScenarioStatus = (typeof scenarioStatusValues)[number];

export const scenarioCreateSchema = z.object({
  name: buildStringSchema(SCENARIO_FIELDS["name"]),
  description: z.string().optional(),
  status: z.enum(scenarioStatusValues).default("active"),
  step_timeout: buildIntSchema(SCENARIO_FIELDS["step_timeout"]),
  validation_timeout: buildIntSchema(SCENARIO_FIELDS["validation_timeout"]),
  steps: z.array(stepSchema).min(SCENARIO_FIELDS["steps"].minItems ?? 1),
  validations: z.array(validationSchema).min(SCENARIO_FIELDS["validations"].minItems ?? 1),
});

export type ScenarioCreate = z.infer<typeof scenarioCreateSchema>;

export const scenarioUpdateSchema = z.object({
  name: buildStringSchema(SCENARIO_FIELDS["name"]).optional(),
  description: z.string().optional(),
  status: z.enum(scenarioStatusValues).optional(),
  step_timeout: buildIntSchema(SCENARIO_FIELDS["step_timeout"]).optional(),
  validation_timeout: buildIntSchema(SCENARIO_FIELDS["validation_timeout"]).optional(),
  steps: z.array(stepSchema).min(SCENARIO_FIELDS["steps"].minItems ?? 1).optional(),
  validations: z.array(validationSchema).min(SCENARIO_FIELDS["validations"].minItems ?? 1).optional(),
});

export type ScenarioUpdate = z.infer<typeof scenarioUpdateSchema>;

// --- Response schemas (relaxed, no refinements for read safety) ---

const stepResponseSchema = z.object({
  id: z.string(),
  command: z.string(),
  params: z.record(z.string(), z.unknown()).default({}),
});

const urlCheckResponseSchema = z.object({
  match: z.string(),
  value: z.string().nullable().optional(),
});

const paramCheckResponseSchema = z.object({
  key: z.string(),
  match: z.string(),
  value: z.string().nullable().optional(),
});

const validationResponseSchema = z.object({
  id: z.string(),
  provider: z.string().default("custom"),
  url: urlCheckResponseSchema.nullable().optional(),
  params: z.array(paramCheckResponseSchema).default([]),
});

const scenarioResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  status: z.enum(scenarioStatusValues),
  step_timeout: z.number().int(),
  validation_timeout: z.number().int(),
  steps: z.array(stepResponseSchema),
  validations: z.array(validationResponseSchema),
  created_at: z.string(),
  updated_at: z.string(),
});

export type ScenarioResponse = z.infer<typeof scenarioResponseSchema>;

const paginationMetaSchema = z.object({
  page: z.number().int(),
  size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export type PaginationMeta = z.infer<typeof paginationMetaSchema>;

const paginationLinksSchema = z.object({
  self: z.string(),
  first: z.string(),
  last: z.string(),
  next: z.string().nullable(),
  prev: z.string().nullable(),
});

export type PaginationLinks = z.infer<typeof paginationLinksSchema>;

const singleScenarioEnvelopeSchema = z.object({
  data: scenarioResponseSchema,
});

type SingleScenarioEnvelope = z.infer<typeof singleScenarioEnvelopeSchema>;

const scenarioListEnvelopeSchema = z.object({
  data: z.array(scenarioResponseSchema),
  meta: paginationMetaSchema,
  links: paginationLinksSchema,
});

type ScenarioListEnvelope = z.infer<typeof scenarioListEnvelopeSchema>;

const deleteEnvelopeSchema = z.object({
  data: z.object({ id: z.string() }),
});

export type DeleteEnvelope = z.infer<typeof deleteEnvelopeSchema>;

// --- Query params ---

export interface ScenarioListParams {
  name?: string;
  status?: ScenarioStatus;
  sort_by?: SortBy;
  sort_order?: SortOrder;
  page?: number;
  size?: number;
}
