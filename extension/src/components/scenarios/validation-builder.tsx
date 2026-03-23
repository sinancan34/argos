import { useState } from "react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Collapsible } from "radix-ui";
import { ChevronRight, ChevronDown, Trash2 } from "lucide-react";
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
import { PARAM_CHECK_FIELDS, URL_CHECK_FIELDS } from "../../lib/validation-registry";

interface ValidationBuilderProps {
  form: UseFormReturn<ScenarioCreate>;
}

export function ValidationBuilder({ form }: ValidationBuilderProps) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "validations",
  });

  const [closedItems, setClosedItems] = useState<Set<string>>(new Set());
  const isOpen = (id: string) => !closedItems.has(id);
  const toggleItem = (id: string) => {
    setClosedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

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
              url: { match: (URL_CHECK_FIELDS["match"].default ?? "contains") as "contains", value: "" },
              params: [],
            })
          }
        >
          + Add Validation
        </Button>
      </div>

      {fields.map((field, index) => {
        const open = isOpen(field.id);
        const params = form.watch(`validations.${index}.params`);
        const checkCount = params?.length ?? 0;

        return (
          <Collapsible.Root
            key={field.id}
            open={open}
            onOpenChange={() => toggleItem(field.id)}
            className="rounded-md border bg-card"
          >
            <Collapsible.Trigger asChild>
              <button
                type="button"
                className="flex w-full items-center gap-1.5 p-3 text-left"
              >
                {open ? (
                  <ChevronDown className="size-3.5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="size-3.5 text-muted-foreground" />
                )}
                <span className="font-mono text-[10px] text-muted-foreground">
                  VALIDATION {index + 1}
                </span>
                {!open && (
                  <span className="font-mono text-[10px] text-muted-foreground">
                    · {checkCount} check{checkCount !== 1 ? "s" : ""}
                  </span>
                )}
              </button>
            </Collapsible.Trigger>

            <Collapsible.Content className="space-y-2 px-3 pb-3">
              <UrlCheckFields form={form} validationIndex={index} />
              <ValidationParamsBuilder form={form} validationIndex={index} />

              {fields.length > 1 && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground hover:text-destructive"
                  onClick={() => remove(index)}
                >
                  <Trash2 className="size-3.5" />
                  Delete
                </Button>
              )}
            </Collapsible.Content>
          </Collapsible.Root>
        );
      })}

      {form.formState.errors.validations?.root && (
        <p className="text-[11px] text-destructive">
          At least one validation is required
        </p>
      )}
    </div>
  );
}

function UrlCheckFields({
  form,
  validationIndex,
}: {
  form: UseFormReturn<ScenarioCreate>;
  validationIndex: number;
}) {
  const matchValue = form.watch(`validations.${validationIndex}.url.match`);

  return (
    <div className="space-y-1">
      <Label className="text-[11px] text-muted-foreground">URL Check</Label>
      <div className="flex items-center gap-1 rounded border bg-background p-2">
        <Select
          value={matchValue}
          onValueChange={(v) =>
            form.setValue(
              `validations.${validationIndex}.url.match`,
              v as ScenarioCreate["validations"][0]["url"]["match"],
              { shouldDirty: true },
            )
          }
        >
          <SelectTrigger className="h-8 w-[90px] text-[11px]">
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
        {matchValue !== "exists" && (
          <Input
            {...form.register(`validations.${validationIndex}.url.value`)}
            placeholder="https://example.com"
            className="h-8 flex-1 text-[11px]"
          />
        )}
      </div>
      {form.formState.errors.validations?.[validationIndex]?.url && (
        <p className="text-[10px] text-destructive">
          URL value is required
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
        <Label className="text-[11px] text-muted-foreground">Param Checks <span className="font-normal italic">(optional)</span></Label>
        <Button
          type="button"
          variant="ghost"
          size="xs"
          className="text-muted-foreground"
          onClick={() => append({ key: "", match: (PARAM_CHECK_FIELDS["match"].default ?? "exact") as "exact", value: "" })}
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
            <div className="flex items-center gap-1">
              <Input
                {...form.register(
                  `validations.${validationIndex}.params.${paramIndex}.key`,
                )}
                placeholder="key"
                className="h-8 flex-1 text-[11px]"
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
                <SelectTrigger className="h-8 w-[90px] text-[11px]">
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
              {matchValue !== "exists" && (
                <Input
                  {...form.register(
                    `validations.${validationIndex}.params.${paramIndex}.value`,
                  )}
                  placeholder="expected value"
                  className="h-8 flex-1 text-[11px]"
                />
              )}
              <Button
                type="button"
                variant="ghost"
                size="icon-xs"
                className="text-muted-foreground hover:text-destructive"
                onClick={() => remove(paramIndex)}
              >
                &times;
              </Button>
            </div>
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
