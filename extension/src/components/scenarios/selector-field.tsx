import { useState } from "react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { useElementPicker } from "../../lib/hooks/use-element-picker";
import { Crosshair } from "lucide-react";
import type { PickerSelectorResult } from "../../lib/picker/types";

interface SelectorFieldProps {
  value: string;
  onChange: (selector: string) => void;
}

export function SelectorField({ value, onChange }: SelectorFieldProps) {
  const { isPicking, startPicker, cancelPicker } = useElementPicker();
  const [alternatives, setAlternatives] = useState<string[]>([]);

  const handlePick = () => {
    if (isPicking) {
      cancelPicker();
      return;
    }

    setAlternatives([]);
    startPicker((result: PickerSelectorResult) => {
      onChange(result.primary);

      if (result.alternatives.length > 0) {
        setAlternatives(result.alternatives);
      }
    });
  };

  return (
    <div className="space-y-1.5">
      <Label className="text-xs text-muted-foreground">Selector</Label>

      <div className="flex gap-1 items-center">
        <Input
          value={value}
          placeholder="div.my-class"
          className="flex-1 font-mono"
          onChange={(e) => onChange(e.target.value)}
        />

        <Button
          type="button"
          variant={isPicking ? "default" : "ghost"}
          size="icon-xs"
          className={isPicking ? "text-primary-foreground" : "text-muted-foreground"}
          title={isPicking ? "Cancel picker" : "Pick element from page"}
          onClick={handlePick}
        >
          <Crosshair className="h-3.5 w-3.5" />
        </Button>
      </div>

      {alternatives.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {alternatives.map((alt) => (
            <button
              key={alt}
              type="button"
              className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground truncate max-w-[200px]"
              title={alt}
              onClick={() => {
                onChange(alt);
                setAlternatives([]);
              }}
            >
              {alt}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
