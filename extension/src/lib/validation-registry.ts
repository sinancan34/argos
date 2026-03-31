// Validation registry — data sourced from shared/validations.json (single source of truth).

import { z } from "zod/v4";
import validationDefs from "../../../shared/validations.json";
import commandDefs from "../../../shared/commands.json";
import providerDefs from "../../../shared/providers.json";

// --- Types ---

interface FieldDef {
  type: string;
  required?: boolean;
  default?: unknown;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  positive?: boolean;
  minItems?: number;
  source?: string;
  conditionalRequired?: {
    unless: { field: string; equals: string };
    minLength: number;
  };
}

// --- Source resolver ---

function resolveSource(source: string): string[] {
  const [fileKey, fieldKey] = source.split(".");
  if (fileKey === "commands") {
    return (commandDefs as Record<string, unknown>)[fieldKey] as string[];
  }
  throw new Error(`Unknown source: ${source}`);
}

// --- Provider registry ---

export interface ParamSuggestion {
  label: string;
  value: string;
  valueSuggestions: string[];
}

interface ProviderDef {
  name: string;
  urlPatterns: string[];
  paramSuggestions?: ParamSuggestion[];
}

export const PROVIDERS: Record<string, ProviderDef> = providerDefs;
export const PROVIDER_VALUES = ["custom", ...Object.keys(PROVIDERS)] as [string, ...string[]];

// --- Exported constants ---

export const ENUMS = validationDefs.enums;
export const SCENARIO_FIELDS = validationDefs.scenario as Record<string, FieldDef>;
export const URL_CHECK_FIELDS = validationDefs.urlCheck as Record<string, FieldDef>;
export const PARAM_CHECK_FIELDS = validationDefs.paramCheck as Record<string, FieldDef>;

// --- Zod schema builders ---

export function buildStringSchema(def: FieldDef) {
  let s = z.string();
  if (def.minLength !== undefined) s = s.min(def.minLength);
  if (def.maxLength !== undefined) s = s.max(def.maxLength);
  return s;
}

export function buildIntSchema(def: FieldDef) {
  let s = z.number().int();
  if (def.positive) s = s.positive();
  if (def.min !== undefined) s = s.min(def.min);
  if (def.max !== undefined) s = s.max(def.max);
  if (def.default !== undefined) s = s.default(def.default as number);
  return s;
}

export function buildEnumSchema(def: FieldDef) {
  if (!def.source) throw new Error("Enum field requires a 'source'");
  const values = resolveSource(def.source) as [string, ...string[]];
  return z.enum(values);
}

