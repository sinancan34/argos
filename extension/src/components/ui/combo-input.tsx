import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

export interface ComboOption {
  label: string;
  value: string;
}

interface ComboInputProps {
  options: ComboOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function ComboInput({
  options,
  value,
  onChange,
  placeholder,
  className,
}: ComboInputProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const matched = options.find((o) => o.value === value);
  const displayValue = matched ? matched.label : value;

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelect = (option: ComboOption | null) => {
    if (option === null) {
      onChange("");
      setOpen(false);
      inputRef.current?.focus();
    } else {
      onChange(option.value);
      setOpen(false);
    }
  };

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={displayValue}
          placeholder={placeholder}
          className={cn(
            "h-8 w-full min-w-0 rounded-md border border-input bg-transparent px-3 pr-7 py-1 text-xs shadow-xs transition-[color,box-shadow] outline-none placeholder:text-muted-foreground",
            "focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50",
          )}
          onChange={(e) => {
            onChange(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
        />
        <button
          type="button"
          tabIndex={-1}
          className="absolute right-1 top-1/2 -translate-y-1/2 text-muted-foreground"
          onClick={() => {
            setOpen((prev) => !prev);
            inputRef.current?.focus();
          }}
        >
          <ChevronDown className="size-3.5" />
        </button>
      </div>

      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover py-1 shadow-md">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              className={cn(
                "flex w-full items-center px-2 py-1.5 text-xs hover:bg-accent hover:text-accent-foreground",
                option.value === value && "bg-accent/50",
              )}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => handleSelect(option)}
            >
              {option.label}
            </button>
          ))}
          <button
            type="button"
            className="flex w-full items-center px-2 py-1.5 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => handleSelect(null)}
          >
            custom
          </button>
        </div>
      )}
    </div>
  );
}
