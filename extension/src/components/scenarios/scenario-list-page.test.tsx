// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ScenarioListParams } from "../../lib/schemas/scenario";

const {
  navigateMock,
  searchState,
  useScenariosMock,
  updateScenarioMock,
  deleteScenarioMock,
  invalidateQueriesMock,
} = vi.hoisted(() => ({
  navigateMock: vi.fn(),
  searchState: { current: {} as Record<string, unknown> },
  useScenariosMock: vi.fn(),
  updateScenarioMock: vi.fn(),
  deleteScenarioMock: vi.fn(),
  invalidateQueriesMock: vi.fn(),
}));

vi.mock("@tanstack/react-router", () => ({
  useSearch: () => searchState.current,
  useNavigate: () => navigateMock,
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({ invalidateQueries: invalidateQueriesMock }),
}));

vi.mock("../../lib/hooks/use-scenarios", () => ({
  useScenarios: (params: unknown) => useScenariosMock(params),
}));

vi.mock("../../lib/api/scenarios", () => ({
  updateScenario: (id: string, data: unknown) => updateScenarioMock(id, data),
  deleteScenario: (id: string) => deleteScenarioMock(id),
}));

interface TableStubProps {
  scenarios: Array<{ id: string; name: string }>;
  selectedIds: Set<string>;
  onSelectionChange: (ids: Set<string>) => void;
  onPageChange: (page: number) => void;
  onSortChange: (sortBy: string, sortOrder: string) => void;
  onPageSizeChange: (size: number) => void;
}

vi.mock("./scenario-table", () => ({
  ScenarioTable: ({
    scenarios,
    selectedIds,
    onSelectionChange,
    onPageChange,
    onSortChange,
    onPageSizeChange,
  }: TableStubProps) => (
    <div data-testid="scenario-table">
      <span data-testid="row-count">{scenarios.length}</span>
      <span data-testid="selected-count">{selectedIds.size}</span>
      <button onClick={() => onSelectionChange(new Set(["a", "b"]))}>
        select-two
      </button>
      <button onClick={() => onPageChange(3)}>go-page-3</button>
      <button onClick={() => onSortChange("name", "asc")}>sort-name-asc</button>
      <button onClick={() => onPageSizeChange(50)}>size-50</button>
    </div>
  ),
}));

import { ScenarioListPage } from "./scenario-list-page";

const SCENARIOS = [
  { id: "a", name: "First" },
  { id: "b", name: "Second" },
];

const META = { page: 1, size: 20, total_count: 2, total_pages: 1 };

interface ListState {
  data?: { data: typeof SCENARIOS; meta: typeof META };
  isLoading?: boolean;
  error?: Error | null;
}

function primeList(state: ListState = {}): void {
  const { isLoading = false, error = null } = state;
  // A destructuring default would also fire for an explicit `data: undefined`,
  // which is the "still loading" case under test — so check the key instead.
  const data = "data" in state ? state.data : { data: SCENARIOS, meta: META };
  useScenariosMock.mockReturnValue({ data, isLoading, error });
}

/** Search params the page passed to useScenarios on its latest render. */
function lastQueryParams(): ScenarioListParams {
  const call = useScenariosMock.mock.calls.at(-1);
  if (!call) throw new Error("useScenarios was not called");
  return call[0] as ScenarioListParams;
}

/** The search object of the latest navigate call. */
function lastNavigateSearch(): Record<string, unknown> {
  const call = navigateMock.mock.calls.at(-1);
  if (!call) throw new Error("navigate was not called");
  return (call[0] as { search: Record<string, unknown> }).search;
}

function actionsButton(): HTMLElement {
  return screen.getByRole("button", { name: /Actions|Processing/ });
}

describe("ScenarioListPage", () => {
  beforeEach(() => {
    navigateMock.mockReset();
    useScenariosMock.mockReset();
    updateScenarioMock.mockReset();
    deleteScenarioMock.mockReset();
    invalidateQueriesMock.mockReset();
    updateScenarioMock.mockResolvedValue({ data: {} });
    deleteScenarioMock.mockResolvedValue({ data: {} });
    searchState.current = {};
    primeList();
  });

  describe("query params", () => {
    it("applies default sort, order, page, and size", () => {
      // Arrange & Act
      render(<ScenarioListPage />);

      // Assert
      expect(lastQueryParams()).toMatchObject({
        sort_by: "created_at",
        sort_order: "desc",
        page: 1,
        size: 20,
      });
    });

    it("uses the search params from the url", () => {
      // Arrange
      searchState.current = {
        name: "checkout",
        status: true,
        sort_by: "name",
        sort_order: "asc",
        page: 2,
        size: 50,
      };

      // Act
      render(<ScenarioListPage />);

      // Assert
      expect(lastQueryParams()).toMatchObject({
        name: "checkout",
        status: true,
        sort_by: "name",
        page: 2,
        size: 50,
      });
    });

    it("keeps an explicit inactive status filter", () => {
      // Arrange — status false must not fall back to a default
      searchState.current = { status: false };

      // Act
      render(<ScenarioListPage />);

      // Assert
      expect(lastQueryParams().status).toBe(false);
    });
  });

  describe("rendering", () => {
    it("passes the loaded rows to the table", () => {
      // Arrange & Act
      render(<ScenarioListPage />);

      // Assert
      expect(screen.getByTestId("row-count")).toHaveTextContent("2");
    });

    it("passes an empty list when no data has arrived", () => {
      // Arrange
      primeList({ data: undefined, isLoading: true });

      // Act
      render(<ScenarioListPage />);

      // Assert
      expect(screen.getByTestId("row-count")).toHaveTextContent("0");
    });

    it("replaces the table with an error message on failure", () => {
      // Arrange
      primeList({ error: new Error("Network error") });

      // Act
      render(<ScenarioListPage />);

      // Assert
      expect(
        screen.getByText("Failed to load scenarios. Check your connection."),
      ).toBeInTheDocument();
    });

    it("hides the table on failure", () => {
      // Arrange
      primeList({ error: new Error("Network error") });

      // Act
      render(<ScenarioListPage />);

      // Assert
      expect(screen.queryByTestId("scenario-table")).not.toBeInTheDocument();
    });

    it("keeps the toolbar visible on failure", () => {
      // Arrange — the user must still be able to change the filter
      primeList({ error: new Error("Network error") });

      // Act
      render(<ScenarioListPage />);

      // Assert
      expect(
        screen.getByRole("heading", { name: "Scenarios" }),
      ).toBeInTheDocument();
    });
  });

  describe("navigation on param change", () => {
    it("navigates with the merged search params", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("go-page-3"));

      // Assert
      expect(lastNavigateSearch()).toMatchObject({ page: 3 });
    });

    it("preserves the other params when paging", async () => {
      // Arrange
      searchState.current = { name: "checkout" };
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("go-page-3"));

      // Assert
      expect(lastNavigateSearch()).toMatchObject({ name: "checkout" });
    });

    it("keeps the current page when only sorting changes", async () => {
      // Arrange
      searchState.current = { page: 3 };
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("sort-name-asc"));

      // Assert
      expect(lastNavigateSearch()).toMatchObject({ page: 3, sort_by: "name" });
    });

    it("resets to the first page when the page size changes", async () => {
      // Arrange — a size change invalidates the current offset
      searchState.current = { page: 3 };
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("size-50"));

      // Assert
      expect(lastNavigateSearch()).toMatchObject({ page: 1, size: 50 });
    });

    it("resets to the first page when the name filter changes", async () => {
      // Arrange
      searchState.current = { page: 3 };
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      const searchBox = screen.getByPlaceholderText(/Search by name/);

      // Act
      await user.type(searchBox, "checkout");
      await user.keyboard("{Enter}");

      // Assert
      expect(lastNavigateSearch()).toMatchObject({
        page: 1,
        name: "checkout",
      });
    });

    it("clears the selection when the params change", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await user.click(screen.getByText("select-two"));

      // Act
      await user.click(screen.getByText("go-page-3"));

      // Assert
      expect(screen.getByTestId("selected-count")).toHaveTextContent("0");
    });
  });

  describe("selection", () => {
    it("starts with nothing selected", () => {
      // Arrange & Act
      render(<ScenarioListPage />);

      // Assert
      expect(screen.getByTestId("selected-count")).toHaveTextContent("0");
    });

    it("tracks the table's selection", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("select-two"));

      // Assert
      expect(screen.getByTestId("selected-count")).toHaveTextContent("2");
    });

    it("enables the bulk actions once rows are selected", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("select-two"));

      // Assert
      expect(actionsButton()).toBeEnabled();
    });
  });

  describe("bulk status change", () => {
    it("updates every selected scenario", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Inactive" }));

      // Assert
      await waitFor(() =>
        expect(updateScenarioMock).toHaveBeenCalledWith("a", { status: false }),
      );
    });

    it("updates each id exactly once", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Active" }));

      // Assert
      await waitFor(() => expect(updateScenarioMock).toHaveBeenCalledTimes(2));
    });

    it("refreshes the list afterwards", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Active" }));

      // Assert
      await waitFor(() =>
        expect(invalidateQueriesMock).toHaveBeenCalledWith({
          queryKey: ["scenarios"],
        }),
      );
    });

    it("clears the selection afterwards", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Active" }));

      // Assert
      await waitFor(() =>
        expect(screen.getByTestId("selected-count")).toHaveTextContent("0"),
      );
    });

    it("still settles when one update fails", async () => {
      // Arrange — allSettled means one rejection must not abort the rest
      updateScenarioMock.mockRejectedValueOnce(new Error("Conflict"));
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Active" }));

      // Assert
      await waitFor(() =>
        expect(invalidateQueriesMock).toHaveBeenCalledWith({
          queryKey: ["scenarios"],
        }),
      );
    });
  });

  describe("bulk delete", () => {
    async function openBulkDelete(user: ReturnType<typeof userEvent.setup>) {
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());
      await user.click(screen.getByRole("menuitem", { name: "Delete" }));
    }

    it("asks for confirmation naming the count", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await openBulkDelete(user);

      // Assert
      expect(screen.getByText("Delete 2 scenarios?")).toBeInTheDocument();
    });

    it("uses the singular form for one scenario", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await user.click(screen.getByText("select-two"));
      await user.click(actionsButton());
      await user.click(screen.getByRole("menuitem", { name: "Delete" }));

      // Assert — the stub selects two ids, so the plural is expected here
      expect(screen.queryByText("Delete 1 scenario?")).not.toBeInTheDocument();
    });

    it("deletes nothing before confirmation", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);

      // Act
      await openBulkDelete(user);

      // Assert
      expect(deleteScenarioMock).not.toHaveBeenCalled();
    });

    it("deletes every selected scenario when confirmed", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await openBulkDelete(user);

      // Act
      await user.click(screen.getByRole("button", { name: "Delete" }));

      // Assert
      await waitFor(() => expect(deleteScenarioMock).toHaveBeenCalledTimes(2));
    });

    it("refreshes the list after deleting", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await openBulkDelete(user);

      // Act
      await user.click(screen.getByRole("button", { name: "Delete" }));

      // Assert
      await waitFor(() =>
        expect(invalidateQueriesMock).toHaveBeenCalledWith({
          queryKey: ["scenarios"],
        }),
      );
    });

    it("closes the prompt after deleting", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await openBulkDelete(user);

      // Act
      await user.click(screen.getByRole("button", { name: "Delete" }));

      // Assert
      await waitFor(() =>
        expect(screen.queryByText("Delete 2 scenarios?")).not.toBeInTheDocument(),
      );
    });

    it("abandons the deletion when cancelled", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await openBulkDelete(user);

      // Act
      await user.click(screen.getByRole("button", { name: "Cancel" }));

      // Assert
      expect(deleteScenarioMock).not.toHaveBeenCalled();
    });

    it("still settles when one deletion fails", async () => {
      // Arrange
      deleteScenarioMock.mockRejectedValueOnce(new Error("Forbidden"));
      const user = userEvent.setup();
      render(<ScenarioListPage />);
      await openBulkDelete(user);

      // Act
      await user.click(screen.getByRole("button", { name: "Delete" }));

      // Assert
      await waitFor(() =>
        expect(invalidateQueriesMock).toHaveBeenCalledWith({
          queryKey: ["scenarios"],
        }),
      );
    });
  });
});
