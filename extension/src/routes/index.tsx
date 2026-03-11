import { createRoute } from "@tanstack/react-router";
import { rootRoute } from "./__root";
import { ScenarioListPage } from "../components/scenarios/scenario-list-page";
import type { SortBy, SortOrder } from "../lib/schemas/scenario";

type SearchParams = {
  name?: string;
  status?: number;
  sort_by?: SortBy;
  sort_order?: SortOrder;
  page?: number;
  size?: number;
};

export const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  validateSearch: (search: Record<string, unknown>): SearchParams => ({
    name: (search.name as string) || undefined,
    status: search.status !== undefined ? Number(search.status) : undefined,
    sort_by: (search.sort_by as SortBy) || undefined,
    sort_order: (search.sort_order as SortOrder) || undefined,
    page: search.page ? Number(search.page) : undefined,
    size: search.size ? Number(search.size) : undefined,
  }),
  component: ScenarioListPage,
});
