import { useFieldArray, type UseFormReturn } from "react-hook-form";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { CommandParamsFields } from "./command-params-fields";
import { COMMAND_CATEGORIES } from "../../lib/commands";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

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
            append({
              id: crypto.randomUUID(),
              command: "" as never,
              params: {},
            })
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
            <Select
              value={form.watch(`steps.${index}.command`)}
              onValueChange={(v) =>
                form.setValue(`steps.${index}.command`, v as ScenarioCreate["steps"][number]["command"], {
                  shouldDirty: true,
                })
              }
            >
              <SelectTrigger size="sm" className="mt-0.5 w-full text-xs">
                <SelectValue placeholder="Select command..." />
              </SelectTrigger>
              <SelectContent>
                {COMMAND_CATEGORIES.map((cat) => (
                  <SelectGroup key={cat.category}>
                    <SelectLabel>{cat.category}</SelectLabel>
                    {cat.commands.map((cmd) => (
                      <SelectItem
                        key={cmd.command}
                        value={cmd.command}
                        className="text-xs"
                      >
                        {cmd.command}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                ))}
              </SelectContent>
            </Select>
            {form.formState.errors.steps?.[index]?.command && (
              <p className="mt-0.5 text-[10px] text-destructive">
                Command is required
              </p>
            )}
          </div>

          <CommandParamsFields form={form} stepIndex={index} />

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
              className="mt-0.5 h-8 font-mono text-xs"
            />
          </div>
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
