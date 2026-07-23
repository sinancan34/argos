import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "@tanstack/react-router";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Separator } from "../ui/separator";
import { DeviceSelect } from "./device-select";
import { StepBuilder } from "./step-builder";
import { ValidationBuilder } from "./validation-builder";
import {
  scenarioCreateSchema,
  scenarioUpdateSchema,
  type ScenarioCreate,
  type ScenarioUpdate,
  type ScenarioResponse,
} from "../../lib/schemas/scenario";
import {
  SCENARIO_FIELDS,
  URL_CHECK_FIELDS,
} from "../../lib/validation-registry";

/** Recursively replace `null` with `undefined` so Zod `.optional()` accepts API data. */
function nullToUndefined<T>(value: T): T {
  if (value === null) return undefined as unknown as T;
  if (Array.isArray(value)) return value.map(nullToUndefined) as unknown as T;
  if (typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [
        k,
        nullToUndefined(v),
      ]),
    ) as T;
  }
  return value;
}

interface ScenarioFormProps {
  mode: "create" | "edit";
  defaultValues?: ScenarioResponse;
  onSubmit: (data: ScenarioCreate | ScenarioUpdate) => void;
  isSubmitting: boolean;
}

export function ScenarioForm({
  mode,
  defaultValues,
  onSubmit,
  isSubmitting,
}: ScenarioFormProps) {
  const navigate = useNavigate();

  const schema = mode === "edit" ? scenarioUpdateSchema : scenarioCreateSchema;
  const form = useForm<ScenarioCreate>({
    // `schema` is a create|update union and status carries a Zod default, so the
    // resolver's inferred transform type diverges from ScenarioCreate. Pin it.
    resolver: zodResolver(schema) as Resolver<ScenarioCreate>,
    defaultValues: defaultValues
      ? {
          name: defaultValues.name,
          description: defaultValues.description ?? "",
          status: defaultValues.status,
          device_id: defaultValues.device_id,
          step_timeout: defaultValues.step_timeout,
          validation_timeout: defaultValues.validation_timeout,
          steps: nullToUndefined(defaultValues.steps) as ScenarioCreate["steps"],
          validations: nullToUndefined(defaultValues.validations) as ScenarioCreate["validations"],
        }
      : {
          name: "",
          description: "",
          status: (SCENARIO_FIELDS["status"].default ?? true) as boolean,
          device_id: "",
          step_timeout: (SCENARIO_FIELDS["step_timeout"].default ?? 5000) as number,
          validation_timeout: (SCENARIO_FIELDS["validation_timeout"].default ?? 10000) as number,
          steps: [{ id: crypto.randomUUID(), command: "" as never, params: {} }],
          validations: [
            {
              id: crypto.randomUUID(),
              provider: "custom" as const,
              url: { match: (URL_CHECK_FIELDS["match"].default ?? "contains") as "contains", value: "" },
              params: [],
            },
          ],
        },
  });

  const handleFormSubmit = (data: ScenarioCreate) => {
    if (mode === "edit" && defaultValues) {
      const dirtyFields = form.formState.dirtyFields;
      const update: ScenarioUpdate = {};

      if (dirtyFields.name) update.name = data.name;
      if (dirtyFields.description) update.description = data.description;
      if (dirtyFields.status) update.status = data.status;
      if (dirtyFields.device_id) update.device_id = data.device_id;
      if (dirtyFields.step_timeout) update.step_timeout = data.step_timeout;
      if (dirtyFields.validation_timeout) update.validation_timeout = data.validation_timeout;

      const defaultSteps = defaultValues.steps as ScenarioCreate["steps"];
      const defaultValidations = defaultValues.validations as ScenarioCreate["validations"];

      if (dirtyFields.steps || data.steps.length !== defaultSteps.length) {
        update.steps = data.steps;
      }
      if (dirtyFields.validations || data.validations.length !== defaultValidations.length) {
        update.validations = data.validations;
      }

      onSubmit(update);
    } else {
      onSubmit(data);
    }
  };

  const hasErrors = Object.keys(form.formState.errors).length > 0;

  return (
    <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-4">
      <div className="space-y-3">
        <div>
          <Label htmlFor="name" className="text-xs font-medium">
            Name <span className="text-destructive">*</span>
          </Label>
          <Input
            id="name"
            {...form.register("name")}
            placeholder="e.g. Purchase Event Pixel Check"
            className="mt-1"
          />
          {form.formState.errors.name && (
            <p className="mt-1 text-xs text-destructive">
              {form.formState.errors.name.message}
            </p>
          )}
        </div>

        <div>
          <Label htmlFor="description" className="text-xs font-medium">
            Description
          </Label>
          <Textarea
            id="description"
            {...form.register("description")}
            placeholder="Optional description..."
            className="mt-1 min-h-[60px] resize-none text-xs lg:min-h-[90px]"
          />
        </div>

        <div>
          <Label htmlFor="device_id" className="text-xs font-medium">
            Device <span className="text-destructive">*</span>
          </Label>
          <DeviceSelect
            value={form.watch("device_id")}
            onChange={(id) =>
              form.setValue("device_id", id, {
                shouldDirty: true,
                shouldValidate: true,
              })
            }
            hasError={!!form.formState.errors.device_id}
            className="mt-1"
          />
          {form.formState.errors.device_id && (
            <p className="mt-1 text-xs text-destructive">
              {form.formState.errors.device_id.message}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <Label htmlFor="step_timeout" className="text-xs font-medium">
              Step Timeout (ms)
            </Label>
            <Input
              id="step_timeout"
              type="number"
              {...form.register("step_timeout", {
                setValueAs: (v) => (v === "" ? undefined : Number(v)),
              })}
              className="mt-1 font-mono"
            />
          </div>
          <div>
            <Label htmlFor="validation_timeout" className="text-xs font-medium">
              Validation Timeout (ms)
            </Label>
            <Input
              id="validation_timeout"
              type="number"
              {...form.register("validation_timeout", {
                setValueAs: (v) => (v === "" ? undefined : Number(v)),
              })}
              className="mt-1 font-mono"
            />
          </div>
        </div>
      </div>

      <Separator />

      <StepBuilder form={form} />

      <Separator />

      <ValidationBuilder form={form} />

      <Separator />

      {hasErrors && (
        <p className="text-xs text-destructive">
          Please fix the validation errors above before saving.
        </p>
      )}

      <div className="flex gap-2 pb-4">
        <Button type="submit" size="sm" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : mode === "create" ? "Create Scenario" : "Save Changes"}
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => navigate({ to: "/" })}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
