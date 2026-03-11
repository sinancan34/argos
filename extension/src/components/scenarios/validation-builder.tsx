import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { matchTypeValues, type ScenarioCreate } from "../../lib/schemas/scenario";

interface ValidationBuilderProps {
  form: UseFormReturn<ScenarioCreate>;
}

export function ValidationBuilder({ form }: ValidationBuilderProps) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "validations",
  });

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Validations
        </Label>
        <Button
          type="button"
          variant="outline"
          size="xs"
          onClick={() =>
            append({
              id: crypto.randomUUID(),
              params: [{ key: "", match: "exact", value: "" }],
            })
          }
        >
          + Add Validation
        </Button>
      </div>

      {fields.map((field, index) => (
        <div
          key={field.id}
          className="relative rounded-md border bg-card p-3 space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-muted-foreground">
              VALIDATION {index + 1}
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

          <ValidationParamsBuilder form={form} validationIndex={index} />
        </div>
      ))}

      {form.formState.errors.validations?.root && (
        <p className="text-[11px] text-destructive">
          At least one validation is required
        </p>
      )}
    </div>
  );
}

function ValidationParamsBuilder({
  form,
  validationIndex,
}: {
  form: UseFormReturn<ScenarioCreate>;
  validationIndex: number;
}) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: `validations.${validationIndex}.params`,
  });

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-[11px] text-muted-foreground">Param Checks</Label>
        <Button
          type="button"
          variant="ghost"
          size="xs"
          className="text-muted-foreground"
          onClick={() => append({ key: "", match: "exact", value: "" })}
        >
          + check
        </Button>
      </div>

      {fields.map((field, paramIndex) => {
        const matchValue = form.watch(
          `validations.${validationIndex}.params.${paramIndex}.match`,
        );

        return (
          <div key={field.id} className="space-y-1 rounded border bg-background p-2">
            <div className="flex gap-1">
              <Input
                {...form.register(
                  `validations.${validationIndex}.params.${paramIndex}.key`,
                )}
                placeholder="key"
                className="h-6 flex-1 text-[11px]"
              />
              <Select
                value={matchValue}
                onValueChange={(v) =>
                  form.setValue(
                    `validations.${validationIndex}.params.${paramIndex}.match`,
                    v as ScenarioCreate["validations"][0]["params"][0]["match"],
                    { shouldDirty: true },
                  )
                }
              >
                <SelectTrigger className="h-6 w-[90px] text-[11px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {matchTypeValues.map((mt) => (
                    <SelectItem key={mt} value={mt} className="text-[11px]">
                      {mt}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {fields.length > 1 && (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-xs"
                  className="text-muted-foreground hover:text-destructive"
                  onClick={() => remove(paramIndex)}
                >
                  &times;
                </Button>
              )}
            </div>
            {matchValue !== "exists" && (
              <Input
                {...form.register(
                  `validations.${validationIndex}.params.${paramIndex}.value`,
                )}
                placeholder="expected value"
                className="h-6 text-[11px]"
              />
            )}
            {form.formState.errors.validations?.[validationIndex]?.params?.[
              paramIndex
            ] && (
              <p className="text-[10px] text-destructive">
                Check all required fields
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
