import { z } from "zod/v4";
import commandDefs from "../../../../shared/commands.json";
import { commandValues } from "../commands";
import {
  ENUMS,
  SCENARIO_FIELDS,
  PARAM_CHECK_FIELDS,
  buildStringSchema,
  buildIntSchema,
  buildEnumSchema,
} from "../validation-registry";

// --- Enums (sourced from shared sources) ---

export const matchTypeValues = commandDefs.matchTypes as [string, ...string[]];

export const matchTypeSchema = z.enum(matchTypeValues);
export type MatchType = z.infer<typeof matchTypeSchema>;

export const sortByValues = ENUMS.sortBy as [string, ...string[]];
export const sortBySchema = z.enum(sortByValues);
export type SortBy = z.infer<typeof sortBySchema>;

export const sortOrderValues = ENUMS.sortOrder as [string, ...string[]];
export const sortOrderSchema = z.enum(sortOrderValues);
export type SortOrder = z.infer<typeof sortOrderSchema>;

// --- Nested schemas ---

const _pcKeySch = buildStringSchema(PARAM_CHECK_FIELDS["key"]);
const _pcMatchSch = buildEnumSchema(PARAM_CHECK_FIELDS["match"]);
const _pcCond = PARAM_CHECK_FIELDS["value"].conditionalRequired!;

export const paramCheckSchema = z
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

export type ParamCheck = z.infer<typeof paramCheckSchema>;

export const stepSchema = z.object({
  id: z.string(),
  command: z.enum(commandValues),
  params: z.record(z.string(), z.unknown()).default({}),
});

export type Step = z.infer<typeof stepSchema>;

export const validationSchema = z.object({
  id: z.string(),
  params: z.array(paramCheckSchema).min(SCENARIO_FIELDS["validations"].minItems ?? 1),
});

export type Validation = z.infer<typeof validationSchema>;

// --- Request schemas ---

export const scenarioCreateSchema = z.object({
  name: buildStringSchema(SCENARIO_FIELDS["name"]),
  description: z.string().optional(),
  status: buildIntSchema(SCENARIO_FIELDS["status"]),
  step_timeout: buildIntSchema(SCENARIO_FIELDS["step_timeout"]),
  validation_timeout: buildIntSchema(SCENARIO_FIELDS["validation_timeout"]),
  steps: z.array(stepSchema).min(SCENARIO_FIELDS["steps"].minItems ?? 1),
  validations: z.array(validationSchema).min(SCENARIO_FIELDS["validations"].minItems ?? 1),
});

export type ScenarioCreate = z.infer<typeof scenarioCreateSchema>;

export const scenarioUpdateSchema = z.object({
  name: buildStringSchema(SCENARIO_FIELDS["name"]).optional(),
  description: z.string().optional(),
  status: z.number().int().optional(),
  step_timeout: buildIntSchema(SCENARIO_FIELDS["step_timeout"]).optional(),
  validation_timeout: buildIntSchema(SCENARIO_FIELDS["validation_timeout"]).optional(),
  steps: z.array(stepSchema).min(SCENARIO_FIELDS["steps"].minItems ?? 1).optional(),
  validations: z.array(validationSchema).min(SCENARIO_FIELDS["validations"].minItems ?? 1).optional(),
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
