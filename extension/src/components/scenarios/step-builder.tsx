import { useState } from "react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

interface ParamEntry {
  key: string;
  value: string;
}

interface StepBuilderProps {
  form: UseFormReturn<ScenarioCreate>;
}

export function StepBuilder({ form }: StepBuilderProps) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "steps",
  });

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Steps
        </Label>
        <Button
          type="button"
          variant="outline"
          size="xs"
          onClick={() =>
            append({ id: crypto.randomUUID(), command: "", params: {} })
          }
        >
          + Add Step
        </Button>
      </div>

      {fields.map((field, index) => (
        <div
          key={field.id}
          className="relative rounded-md border bg-card p-3 space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-muted-foreground">
              STEP {index + 1}
            </span>
            {fields.length > 1 && (
              <Button
                type="button"
                variant="ghost"
                size="icon-xs"
                className="text-muted-foreground hover:text-destructive"
                onClick={() => remove(index)}
              >
                &times;
              </Button>
            )}
          </div>

          <div>
            <Label className="text-[11px] text-muted-foreground">Command</Label>
            <Input
              {...form.register(`steps.${index}.command`)}
              placeholder="e.g. navigate, click, wait"
              className="mt-0.5 h-7 text-xs"
            />
            {form.formState.errors.steps?.[index]?.command && (
              <p className="mt-0.5 text-[10px] text-destructive">
                Command is required
              </p>
            )}
          </div>

          <div>
            <Label className="text-[11px] text-muted-foreground">
              Timeout (ms, optional)
            </Label>
            <Input
              type="number"
              {...form.register(`steps.${index}.timeout`, {
                setValueAs: (v) => (v === "" ? undefined : Number(v)),
              })}
              placeholder="Override default"
              className="mt-0.5 h-7 font-mono text-xs"
            />
          </div>

          <StepParamsBuilder form={form} stepIndex={index} />
        </div>
      ))}

      {form.formState.errors.steps?.root && (
        <p className="text-[11px] text-destructive">
          At least one step is required
        </p>
      )}
    </div>
  );
}

function StepParamsBuilder({
  form,
  stepIndex,
}: {
  form: UseFormReturn<ScenarioCreate>;
  stepIndex: number;
}) {
  const currentParams = form.watch(`steps.${stepIndex}.params`) || {};

  const toEntries = (obj: Record<string, unknown>): ParamEntry[] =>
    Object.entries(obj).map(([key, value]) => ({ key, value: String(value ?? "") }));

  const [entries, setEntries] = useState<ParamEntry[]>(() => toEntries(currentParams));

  const syncToForm = (updated: ParamEntry[]) => {
    const obj: Record<string, unknown> = {};
    for (const entry of updated) {
      if (entry.key) obj[entry.key] = entry.value;
    }
    form.setValue(`steps.${stepIndex}.params`, obj, { shouldDirty: true });
  };

  const addParam = () => {
    const updated = [...entries, { key: "", value: "" }];
    setEntries(updated);
  };

  const updateEntry = (index: number, field: "key" | "value", val: string) => {
    const updated = entries.map((e, i) => (i === index ? { ...e, [field]: val } : e));
    setEntries(updated);
    syncToForm(updated);
  };

  const removeEntry = (index: number) => {
    const updated = entries.filter((_, i) => i !== index);
    setEntries(updated);
    syncToForm(updated);
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <Label className="text-[11px] text-muted-foreground">Params</Label>
        <Button
          type="button"
          variant="ghost"
          size="xs"
          className="text-muted-foreground"
          onClick={addParam}
        >
          + param
        </Button>
      </div>
      {entries.map((entry, i) => (
        <div key={i} className="flex gap-1">
          <Input
            value={entry.key}
            placeholder="key"
            className="h-6 flex-1 text-[11px]"
            onChange={(e) => updateEntry(i, "key", e.target.value)}
          />
          <Input
            value={entry.value}
            placeholder="value"
            className="h-6 flex-1 text-[11px]"
            onChange={(e) => updateEntry(i, "value", e.target.value)}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon-xs"
            className="text-muted-foreground hover:text-destructive"
            onClick={() => removeEntry(i)}
          >
            &times;
          </Button>
        </div>
      ))}
    </div>
  );
}
