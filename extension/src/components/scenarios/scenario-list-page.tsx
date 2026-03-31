import { useCallback, useRef, useState } from "react";
import { useSearch, useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import { useScenarios } from "../../lib/hooks/use-scenarios";
import { updateScenario, deleteScenario } from "../../lib/api/scenarios";
import { TableToolbar } from "./table-toolbar";
import { ScenarioTable } from "./scenario-table";
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
import type { ScenarioListParams, SortBy, SortOrder } from "../../lib/schemas/scenario";

export function ScenarioListPage() {
  const search = useSearch({ from: "/" });
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isBulkActionPending, setIsBulkActionPending] = useState(false);
  const [bulkDeleteTarget, setBulkDeleteTarget] = useState<string[] | null>(null);

  const params: ScenarioListParams = {
    name: search.name,
    status: search.status,
    sort_by: search.sort_by || "created_at",
    sort_order: search.sort_order || "desc",
    page: search.page || 1,
    size: search.size || 20,
  };

  const paramsRef = useRef(params);
  paramsRef.current = params;

  const { data, isLoading, error } = useScenarios(params);

  const updateSearch = useCallback(
    (updates: Partial<ScenarioListParams>) => {
      const current = paramsRef.current;
      const resetPage = "name" in updates || "status" in updates || "size" in updates;
      setSelectedIds(new Set());
      navigate({
        to: "/",
        search: {
          ...current,
          ...updates,
          ...(resetPage ? { page: 1 } : {}),
        },
      });
    },
    [navigate],
  );

  const handleSortChange = useCallback(
    (sortBy: SortBy, sortOrder: SortOrder) => {
      updateSearch({ sort_by: sortBy, sort_order: sortOrder });
    },
    [updateSearch],
  );

  const handlePageSizeChange = useCallback(
    (size: number) => {
      updateSearch({ size });
    },
    [updateSearch],
  );

  const handleBulkStatusChange = useCallback(
    async (ids: string[], status: number) => {
      setIsBulkActionPending(true);
      try {
        await Promise.allSettled(
          ids.map((id) => updateScenario(id, { status })),
        );
        setSelectedIds(new Set());
        queryClient.invalidateQueries({ queryKey: ["scenarios"] });
      } finally {
        setIsBulkActionPending(false);
      }
    },
    [queryClient],
  );

  const handleBulkDelete = useCallback((ids: string[]) => {
    setBulkDeleteTarget(ids);
  }, []);

  const confirmBulkDelete = async () => {
    if (!bulkDeleteTarget) return;
    setIsBulkActionPending(true);
    try {
      await Promise.allSettled(
        bulkDeleteTarget.map((id) => deleteScenario(id)),
      );
      setSelectedIds(new Set());
      setBulkDeleteTarget(null);
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    } finally {
      setIsBulkActionPending(false);
    }
  };

  return (
    <div className="space-y-3">
      <TableToolbar
        params={params}
        onParamsChange={updateSearch}
        selectedIds={selectedIds}
        onBulkStatusChange={handleBulkStatusChange}
        onBulkDelete={handleBulkDelete}
        isBulkActionPending={isBulkActionPending}
      />

      {error ? (
        <div className="rounded-md border border-destructive/30 bg-destructive/5 px-4 py-6 text-center text-sm text-destructive">
          Failed to load scenarios. Check your connection.
        </div>
      ) : (
        <ScenarioTable
          scenarios={data?.data ?? []}
          meta={data?.meta}
          isLoading={isLoading}
          page={params.page ?? 1}
          onPageChange={(page) => updateSearch({ page })}
          pageSize={params.size ?? 20}
          onPageSizeChange={handlePageSizeChange}
          sortBy={(params.sort_by ?? "created_at") as SortBy}
          sortOrder={(params.sort_order ?? "desc") as SortOrder}
          onSortChange={handleSortChange}
          selectedIds={selectedIds}
          onSelectionChange={setSelectedIds}
        />
      )}

      <AlertDialog
        open={!!bulkDeleteTarget}
        onOpenChange={(open) => !open && setBulkDeleteTarget(null)}
      >
        <AlertDialogContent className="max-w-sm">
          <AlertDialogHeader>
            <AlertDialogTitle>
              Delete {bulkDeleteTarget?.length} scenario{(bulkDeleteTarget?.length ?? 0) > 1 ? "s" : ""}?
            </AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the selected scenarios. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel size="sm">Cancel</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              size="sm"
              onClick={confirmBulkDelete}
              disabled={isBulkActionPending}
            >
              {isBulkActionPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
