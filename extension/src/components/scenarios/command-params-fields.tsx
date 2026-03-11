import { useEffect, useRef } from "react";
import type { UseFormReturn } from "react-hook-form";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { SelectorField } from "./selector-field";
import { COMMAND_MAP, type SelectorEntry } from "../../lib/commands";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

interface CommandParamsFieldsProps {
  form: UseFormReturn<ScenarioCreate>;
  stepIndex: number;
}

export function CommandParamsFields({
  form,
  stepIndex,
}: CommandParamsFieldsProps) {
  const command = form.watch(`steps.${stepIndex}.command`);
  const prevCommandRef = useRef(command);

  // Reset params when command changes (but not on initial mount)
  useEffect(() => {
    if (prevCommandRef.current !== command) {
      prevCommandRef.current = command;
      const def = COMMAND_MAP.get(command);
      if (def) {
        const defaults: Record<string, unknown> = {};
        for (const p of def.params) {
          if (p.type === "selector") {
            defaults[p.name] = [{ strategy: "css", value: "" }];
          } else if (p.type === "int") {
            defaults[p.name] = undefined;
          } else {
            defaults[p.name] = "";
          }
        }
        form.setValue(`steps.${stepIndex}.params`, defaults, {
          shouldDirty: true,
        });
      }
    }
  }, [command, form, stepIndex]);

  const def = COMMAND_MAP.get(command);
  if (!def || def.params.length === 0) return null;

  const params =
    (form.watch(`steps.${stepIndex}.params`) as Record<string, unknown>) || {};

  const setParam = (name: string, value: unknown) => {
    form.setValue(
      `steps.${stepIndex}.params`,
      { ...params, [name]: value },
      { shouldDirty: true },
    );
  };

  return (
    <div className="space-y-2">
      {def.params.map((paramDef) => {
        if (paramDef.type === "selector") {
          const selectors = (params[paramDef.name] as SelectorEntry[]) || [
            { strategy: "css", value: "" },
          ];
          return (
            <SelectorField
              key={paramDef.name}
              value={selectors}
              onChange={(v) => setParam(paramDef.name, v)}
            />
          );
        }

        if (paramDef.type === "int") {
          return (
            <div key={paramDef.name}>
              <Label className="text-[11px] text-muted-foreground">
                {paramDef.name}
                {paramDef.required && (
                  <span className="text-destructive"> *</span>
                )}
              </Label>
              <Input
                type="number"
                value={params[paramDef.name] != null ? String(params[paramDef.name]) : ""}
                placeholder={paramDef.placeholder}
                className="mt-0.5 h-8 font-mono text-xs"
                onChange={(e) =>
                  setParam(
                    paramDef.name,
                    e.target.value === "" ? undefined : Number(e.target.value),
                  )
                }
              />
            </div>
          );
        }

        // string type
        return (
          <div key={paramDef.name}>
            <Label className="text-[11px] text-muted-foreground">
              {paramDef.name}
              {paramDef.required && (
                <span className="text-destructive"> *</span>
              )}
            </Label>
            <Input
              value={(params[paramDef.name] as string) ?? ""}
              placeholder={paramDef.placeholder}
              className="mt-0.5 h-8 text-xs"
              onChange={(e) => setParam(paramDef.name, e.target.value)}
            />
          </div>
        );
      })}
    </div>
  );
}
