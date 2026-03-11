import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import {
  selectorStrategies,
  type SelectorEntry,
  type SelectorStrategy,
} from "../../lib/commands";

interface SelectorFieldProps {
  value: SelectorEntry[];
  onChange: (selectors: SelectorEntry[]) => void;
}

export function SelectorField({ value, onChange }: SelectorFieldProps) {
  const addSelector = () => {
    onChange([...value, { strategy: "css", value: "" }]);
  };

  const updateSelector = (
    index: number,
    field: "strategy" | "value",
    val: string,
  ) => {
    const updated = value.map((s, i) =>
      i === index ? { ...s, [field]: val } : s,
    );
    onChange(updated);
  };

  const removeSelector = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <Label className="text-[11px] text-muted-foreground">Selector</Label>
        <Button
          type="button"
          variant="ghost"
          size="xs"
          className="text-muted-foreground"
          onClick={addSelector}
        >
          + fallback
        </Button>
      </div>

      {value.map((entry, i) => (
        <div key={i} className="flex gap-1 items-center">
          <Select
            value={entry.strategy}
            onValueChange={(v) =>
              updateSelector(i, "strategy", v as SelectorStrategy)
            }
          >
            <SelectTrigger size="sm" className="w-[100px] text-xs px-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {selectorStrategies.map((s) => (
                <SelectItem key={s} value={s} className="text-xs">
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Input
            value={entry.value}
            placeholder="selector value"
            className="h-8 flex-1 text-xs"
            onChange={(e) => updateSelector(i, "value", e.target.value)}
          />

          {value.length > 1 && (
            <Button
              type="button"
              variant="ghost"
              size="icon-xs"
              className="text-muted-foreground hover:text-destructive"
              onClick={() => removeSelector(i)}
            >
              &times;
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}
