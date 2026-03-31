import { useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";
import { Switch } from "../ui/switch";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  useDeleteScenario,
  useUpdateScenario,
} from "../../lib/hooks/use-scenarios";
import type {
  PaginationMeta,
  ScenarioResponse,
  SortBy,
  SortOrder,
} from "../../lib/schemas/scenario";
import { ExecutionDialog } from "./execution-dialog";

function getPageNumbers(current: number, total: number): (number | "...")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | "...")[] = [];

  if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i);
    pages.push("...", total);
  } else if (current >= total - 3) {
    pages.push(1, "...");
    for (let i = total - 4; i <= total; i++) pages.push(i);
  } else {
    pages.push(1, "...", current - 1, current, current + 1, "...", total);
  }

  return pages;
}

interface ScenarioTableProps {
  scenarios: ScenarioResponse[];
  meta?: PaginationMeta;
  isLoading: boolean;
  page: number;
  onPageChange: (page: number) => void;
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  sortBy: SortBy;
  sortOrder: SortOrder;
  onSortChange: (sortBy: SortBy, sortOrder: SortOrder) => void;
  selectedIds: Set<string>;
  onSelectionChange: (ids: Set<string>) => void;
}

export function ScenarioTable({
  scenarios,
  meta,
  isLoading,
  page,
  onPageChange,
  pageSize,
  onPageSizeChange,
  sortBy,
  sortOrder,
  onSortChange,
  selectedIds,
  onSelectionChange,
}: ScenarioTableProps) {
  const navigate = useNavigate();
  const deleteMutation = useDeleteScenario();
  const updateMutation = useUpdateScenario();
  const [deleteTarget, setDeleteTarget] = useState<ScenarioResponse | null>(null);
  const [runTarget, setRunTarget] = useState<ScenarioResponse | null>(null);
  const headerCheckboxRef = useRef<HTMLButtonElement>(null);

  const handleSort = () => {
    if (sortBy === "name") {
      if (sortOrder === "asc") {
        onSortChange("name", "desc");
      } else {
        // Third click: back to default (created_at desc)
        onSortChange("created_at", "desc");
      }
    } else {
      onSortChange("name", "asc");
    }
  };

  const handleToggleStatus = (scenario: ScenarioResponse) => {
    updateMutation.mutate({
      id: scenario.id,
      data: { status: scenario.status === "active" ? "inactive" : "active" },
    });
  };

  const handleDelete = () => {
    if (deleteTarget) {
      deleteMutation.mutate(deleteTarget.id, {
        onSuccess: () => setDeleteTarget(null),
      });
    }
  };

  // Selection helpers
  const allOnPageSelected =
    scenarios.length > 0 && scenarios.every((s) => selectedIds.has(s.id));
  const someOnPageSelected =
    scenarios.some((s) => selectedIds.has(s.id)) && !allOnPageSelected;

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const next = new Set(selectedIds);
      for (const s of scenarios) next.add(s.id);
      onSelectionChange(next);
    } else {
      const next = new Set(selectedIds);
      for (const s of scenarios) next.delete(s.id);
      onSelectionChange(next);
    }
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    const next = new Set(selectedIds);
    if (checked) {
      next.add(id);
    } else {
      next.delete(id);
    }
    onSelectionChange(next);
  };

  // Set indeterminate via ref
  if (headerCheckboxRef.current) {
    const input = headerCheckboxRef.current.querySelector("input");
    if (input) input.indeterminate = someOnPageSelected;
  }

  if (isLoading) {
    return (
      <div className="space-y-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-10 animate-pulse rounded-md bg-muted"
            style={{ animationDelay: `${i * 80}ms` }}
          />
        ))}
      </div>
    );
  }

  if (scenarios.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <div className="text-2xl">&#x2205;</div>
        <p className="mt-2 text-sm text-muted-foreground">No scenarios found</p>
        <Button
          variant="outline"
          size="xs"
          className="mt-3"
          onClick={() => navigate({ to: "/scenarios/new" })}
        >
          Create your first scenario
        </Button>
      </div>
    );
  }

  const sortIcon =
    sortBy === "name" ? (
      sortOrder === "asc" ? (
        <ArrowUp className="ml-1 inline h-3 w-3" />
      ) : (
        <ArrowDown className="ml-1 inline h-3 w-3" />
      )
    ) : (
      <ArrowUpDown className="ml-1 inline h-3 w-3 text-muted-foreground/40" />
    );

  return (
    <>
      <div className="overflow-x-auto rounded-md border">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="h-8 w-[40px]">
                <Checkbox
                  checked={allOnPageSelected}
                  onCheckedChange={(checked) => handleSelectAll(!!checked)}
                  aria-label="Select all"
                  data-indeterminate={someOnPageSelected || undefined}
                />
              </TableHead>
              <TableHead
                className="h-8 cursor-pointer select-none text-xs font-medium"
                onClick={handleSort}
              >
                <span className="inline-flex items-center">
                  Name
                  {sortIcon}
                </span>
              </TableHead>
              <TableHead className="h-8 w-auto whitespace-nowrap text-xs font-medium">
                Status
              </TableHead>
              <TableHead className="h-8 w-[60px] text-xs font-medium">
                Actions
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {scenarios.map((scenario) => (
              <TableRow key={scenario.id} className="group">
                <TableCell className="w-[40px] py-2">
                  <Checkbox
                    checked={selectedIds.has(scenario.id)}
                    onCheckedChange={(checked) =>
                      handleSelectOne(scenario.id, !!checked)
                    }
                    aria-label={`Select ${scenario.name}`}
                  />
                </TableCell>
                <TableCell className="max-w-0 truncate py-2 text-xs font-medium">
                  {scenario.name}
                </TableCell>
                <TableCell className="w-auto whitespace-nowrap py-2">
                  <div className="flex items-center gap-1.5">
                    <Switch
                      checked={scenario.status === "active"}
                      onCheckedChange={() => handleToggleStatus(scenario)}
                      size="sm"
                    />
                    <span className="text-xs text-muted-foreground">
                      {scenario.status === "active" ? "Active" : "Inactive"}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="w-[60px] py-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon-xs"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <span className="text-xs">&#x22EE;</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-36">
                      <DropdownMenuItem
                        className="text-xs"
                        onClick={() => setRunTarget(scenario)}
                      >
                        Run
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-xs"
                        onClick={() =>
                          navigate({
                            to: "/scenarios/$scenarioId/edit",
                            params: { scenarioId: scenario.id },
                          })
                        }
                      >
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-xs text-destructive focus:text-destructive"
                        onClick={() => setDeleteTarget(scenario)}
                      >
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {meta && (
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
          <Select
            value={String(pageSize)}
            onValueChange={(v) => onPageSizeChange(Number(v))}
          >
            <SelectTrigger className="w-auto min-w-[80px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10 / page</SelectItem>
              <SelectItem value="20">20 / page</SelectItem>
              <SelectItem value="50">50 / page</SelectItem>
              <SelectItem value="100">100 / page</SelectItem>
            </SelectContent>
          </Select>

          <div className="ml-auto flex items-center gap-1">
            <span className="text-xs text-muted-foreground">
              {meta.total_count} total
            </span>
            <span className="text-muted-foreground">&middot;</span>
            <Button
              variant="outline"
              size="icon-xs"
              disabled={page <= 1}
              onClick={() => onPageChange(1)}
            >
              &laquo;
            </Button>
            <Button
              variant="outline"
              size="icon-xs"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              &lsaquo;
            </Button>
            {getPageNumbers(page, meta.total_pages || 1).map((p, i) =>
              p === "..." ? (
                <span key={`ellipsis-${i}`} className="px-1 text-xs text-muted-foreground">
                  &hellip;
                </span>
              ) : (
                <Button
                  key={p}
                  variant={p === page ? "default" : "outline"}
                  size="icon-xs"
                  onClick={() => onPageChange(p as number)}
                >
                  {p}
                </Button>
              ),
            )}
            <Button
              variant="outline"
              size="icon-xs"
              disabled={page >= (meta.total_pages || 1)}
              onClick={() => onPageChange(page + 1)}
            >
              &rsaquo;
            </Button>
            <Button
              variant="outline"
              size="icon-xs"
              disabled={page >= (meta.total_pages || 1)}
              onClick={() => onPageChange(meta.total_pages || 1)}
            >
              &raquo;
            </Button>
          </div>
        </div>
      )}

      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent className="max-w-sm">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete scenario?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete{" "}
              <span className="font-medium text-foreground">
                {deleteTarget?.name}
              </span>
              . This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel size="sm">Cancel</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <ExecutionDialog
        open={!!runTarget}
        onOpenChange={(open) => !open && setRunTarget(null)}
        scenario={runTarget}
      />
    </>
  );
}
