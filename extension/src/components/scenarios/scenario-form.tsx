import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "@tanstack/react-router";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Separator } from "../ui/separator";
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
    resolver: zodResolver(schema),
    defaultValues: defaultValues
      ? {
          name: defaultValues.name,
          description: defaultValues.description ?? "",
          status: defaultValues.status,
          step_timeout: defaultValues.step_timeout,
          validation_timeout: defaultValues.validation_timeout,
          steps: defaultValues.steps as ScenarioCreate["steps"],
          validations: defaultValues.validations as ScenarioCreate["validations"],
        }
      : {
          name: "",
          description: "",
          status: (SCENARIO_FIELDS["status"].default ?? 1) as number,
          step_timeout: (SCENARIO_FIELDS["step_timeout"].default ?? 5000) as number,
          validation_timeout: (SCENARIO_FIELDS["validation_timeout"].default ?? 10000) as number,
          steps: [{ id: crypto.randomUUID(), command: "" as never, params: {} }],
          validations: [
            {
              id: crypto.randomUUID(),
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
      if (dirtyFields.step_timeout) update.step_timeout = data.step_timeout;
      if (dirtyFields.validation_timeout) update.validation_timeout = data.validation_timeout;
      if (dirtyFields.steps) update.steps = data.steps;
      if (dirtyFields.validations) update.validations = data.validations;

      onSubmit(update);
    } else {
      onSubmit(data);
    }
  };

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
            className="mt-1 h-8 text-xs"
          />
          {form.formState.errors.name && (
            <p className="mt-1 text-[11px] text-destructive">
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
            className="mt-1 min-h-[60px] resize-none text-xs"
          />
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
              className="mt-1 h-8 font-mono text-xs"
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
              className="mt-1 h-8 font-mono text-xs"
            />
          </div>
        </div>
      </div>

      <Separator />

      <StepBuilder form={form} />

      <Separator />

      <ValidationBuilder form={form} />

      <Separator />

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
