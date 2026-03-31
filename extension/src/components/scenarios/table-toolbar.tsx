import { useState, useEffect } from "react";
import { Link } from "@tanstack/react-router";
import { Input } from "../ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import type { ScenarioListParams } from "../../lib/schemas/scenario";

interface TableToolbarProps {
  params: ScenarioListParams;
  onParamsChange: (updates: Partial<ScenarioListParams>) => void;
  selectedIds: Set<string>;
  onBulkStatusChange: (ids: string[], status: number) => void;
  onBulkDelete: (ids: string[]) => void;
  isBulkActionPending: boolean;
}

export function TableToolbar({
  params,
  onParamsChange,
  selectedIds,
  onBulkStatusChange,
  onBulkDelete,
  isBulkActionPending,
}: TableToolbarProps) {
  const [nameInput, setNameInput] = useState(params.name ?? "");

  useEffect(() => {
    setNameInput(params.name ?? "");
  }, [params.name]);

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Enter") return;
    const value = nameInput.trim();
    if (value === "") {
      onParamsChange({ name: undefined });
    } else if (value.length >= 3) {
      onParamsChange({ name: value });
    }
  };

  const selectedCount = selectedIds.size;
  const selectedArray = Array.from(selectedIds);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h1 className="text-sm font-semibold tracking-tight">Scenarios</h1>
        <Button size="sm" asChild>
          <Link to="/scenarios/new">+ New</Link>
        </Button>
      </div>

      <Input
        placeholder="Search by name (min 3 chars, Enter)..."
        value={nameInput}
        onChange={(e) => setNameInput(e.target.value)}
        onKeyDown={handleSearchKeyDown}
        className="w-full"
      />

      <div className="flex items-center justify-between gap-2">
        <Select
          value={params.status !== undefined ? String(params.status) : "all"}
          onValueChange={(v) =>
            onParamsChange({ status: v === "all" ? undefined : Number(v) })
          }
        >
          <SelectTrigger className="w-auto min-w-[100px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="1">Active</SelectItem>
            <SelectItem value="0">Inactive</SelectItem>
          </SelectContent>
        </Select>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="text-xs"
              disabled={selectedCount === 0 || isBulkActionPending}
            >
              {isBulkActionPending
                ? "Processing..."
                : selectedCount > 0
                  ? `Actions (${selectedCount})`
                  : "Actions"}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40">
            <DropdownMenuItem
              className="text-xs"
              onClick={() => onBulkStatusChange(selectedArray, 1)}
            >
              Active
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-xs"
              onClick={() => onBulkStatusChange(selectedArray, 0)}
            >
              Inactive
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-xs text-destructive focus:text-destructive"
              onClick={() => onBulkDelete(selectedArray)}
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
