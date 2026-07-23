import { useEffect, useRef, useState } from "react";
import { ChevronDown, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { Input } from "../ui/input";
import { useDebounce } from "../../lib/hooks/use-debounce";
import { useDevice, useDevices } from "../../lib/hooks/use-devices";
import { deviceSummary } from "../../lib/devices/device-format";
import type { DeviceResponse } from "../../lib/schemas/device";

interface DeviceSelectProps {
  value: string;
  onChange: (deviceId: string) => void;
  className?: string;
  hasError?: boolean;
}

export function DeviceSelect({
  value,
  onChange,
  className,
  hasError,
}: DeviceSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data, isLoading, isError } = useDevices({
    status: true,
    name: debouncedSearch.trim() || undefined,
    sort_by: "name",
    sort_order: "asc",
    size: 100,
  });
  const devices = data?.data ?? [];

  // Resolve the selected device's name for the trigger, even when the current
  // (filtered) list does not contain it — falls back to a by-id fetch.
  const { data: selectedData } = useDevice(value);
  const selectedDevice =
    devices.find((d) => d.id === value) ?? selectedData?.data ?? null;

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

  const handleSelect = (device: DeviceResponse) => {
    onChange(device.id);
    setOpen(false);
    setSearch("");
  };

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        aria-invalid={hasError || undefined}
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "flex h-8 w-full items-center justify-between gap-2 rounded-md border border-input bg-transparent px-3 py-1 text-xs shadow-xs outline-none transition-[color,box-shadow] dark:bg-input/30",
          "focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50",
          "aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40",
        )}
      >
        <span
          className={cn(
            "truncate",
            !selectedDevice && "text-muted-foreground",
          )}
        >
          {selectedDevice ? selectedDevice.name : "Select device..."}
        </span>
        <ChevronDown className="size-4 shrink-0 opacity-50" />
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
          <div className="relative border-b p-1">
            <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              autoFocus
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search devices..."
              className="h-7 border-0 pl-7 shadow-none focus-visible:ring-0"
            />
          </div>

          <div className="max-h-56 overflow-y-auto py-1">
            {isLoading && (
              <p className="px-2 py-1.5 text-xs text-muted-foreground">
                Loading...
              </p>
            )}
            {isError && (
              <p className="px-2 py-1.5 text-xs text-destructive">
                Failed to load devices
              </p>
            )}
            {!isLoading && !isError && devices.length === 0 && (
              <p className="px-2 py-1.5 text-xs text-muted-foreground">
                No devices found
              </p>
            )}
            {devices.map((device) => {
              const summary = deviceSummary(device);
              return (
                <button
                  key={device.id}
                  type="button"
                  onClick={() => handleSelect(device)}
                  className={cn(
                    "flex w-full items-center justify-between gap-2 px-2 py-1.5 text-left text-xs hover:bg-accent hover:text-accent-foreground",
                    device.id === value && "bg-accent/50",
                  )}
                >
                  <span className="truncate">{device.name}</span>
                  {summary && (
                    <span className="shrink-0 font-mono text-[10px] text-muted-foreground">
                      {summary}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
