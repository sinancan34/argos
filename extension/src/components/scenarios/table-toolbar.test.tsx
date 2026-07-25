// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ScenarioListParams } from "../../lib/schemas/scenario";

interface LinkProps {
  to: string;
  children: React.ReactNode;
}

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: LinkProps) => <a href={to}>{children}</a>,
}));

import { TableToolbar } from "./table-toolbar";

const SEARCH_PLACEHOLDER = "Search by name (min 3 chars, Enter)...";
const MIN_SEARCH_LENGTH = 3;

interface RenderOptions {
  params?: ScenarioListParams;
  selectedIds?: Set<string>;
  isBulkActionPending?: boolean;
}

function renderToolbar({
  params = {},
  selectedIds = new Set<string>(),
  isBulkActionPending = false,
}: RenderOptions = {}) {
  const onParamsChange = vi.fn();
  const onBulkStatusChange = vi.fn();
  const onBulkDelete = vi.fn();

  const view = render(
    <TableToolbar
      params={params}
      onParamsChange={onParamsChange}
      selectedIds={selectedIds}
      onBulkStatusChange={onBulkStatusChange}
      onBulkDelete={onBulkDelete}
      isBulkActionPending={isBulkActionPending}
    />,
  );

  return { ...view, onParamsChange, onBulkStatusChange, onBulkDelete };
}

function searchBox(): HTMLElement {
  return screen.getByPlaceholderText(SEARCH_PLACEHOLDER);
}

/** Types a term into the search box and presses Enter. */
function submitSearch(term: string): void {
  fireEvent.change(searchBox(), { target: { value: term } });
  fireEvent.keyDown(searchBox(), { key: "Enter" });
}

function actionsButton(): HTMLElement {
  return screen.getByRole("button", { name: /Actions|Processing/ });
}

describe("TableToolbar", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("layout", () => {
    it("renders the page heading", () => {
      // Arrange & Act
      renderToolbar();

      // Assert
      expect(screen.getByRole("heading", { name: "Scenarios" })).toBeInTheDocument();
    });

    it("links to the new scenario route", () => {
      // Arrange & Act
      renderToolbar();

      // Assert
      expect(screen.getByRole("link", { name: "+ New" })).toHaveAttribute(
        "href",
        "/scenarios/new",
      );
    });
  });

  describe("search box", () => {
    it("starts empty when no name filter is set", () => {
      // Arrange & Act
      renderToolbar();

      // Assert
      expect(searchBox()).toHaveValue("");
    });

    it("shows the active name filter", () => {
      // Arrange & Act
      renderToolbar({ params: { name: "checkout" } });

      // Assert
      expect(searchBox()).toHaveValue("checkout");
    });

    it("keeps typed text local until Enter is pressed", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      fireEvent.change(searchBox(), { target: { value: "checkout" } });

      // Assert
      expect(onParamsChange).not.toHaveBeenCalled();
    });

    it("reflects typed text in the input immediately", () => {
      // Arrange
      renderToolbar();

      // Act
      fireEvent.change(searchBox(), { target: { value: "checkout" } });

      // Assert
      expect(searchBox()).toHaveValue("checkout");
    });

    it("resyncs the input when the name filter changes externally", () => {
      // Arrange — e.g. the filter is cleared elsewhere in the page
      const { rerender } = renderToolbar({ params: { name: "checkout" } });

      // Act
      rerender(
        <TableToolbar
          params={{ name: "payment" }}
          onParamsChange={vi.fn()}
          selectedIds={new Set()}
          onBulkStatusChange={vi.fn()}
          onBulkDelete={vi.fn()}
          isBulkActionPending={false}
        />,
      );

      // Assert
      expect(searchBox()).toHaveValue("payment");
    });

    it("submits a term at the minimum length", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("a".repeat(MIN_SEARCH_LENGTH));

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: "aaa" });
    });

    it("submits a longer term", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("checkout");

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: "checkout" });
    });

    it("ignores a term one character below the minimum", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("ab");

      // Assert
      expect(onParamsChange).not.toHaveBeenCalled();
    });

    it("ignores a single-character term", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("a");

      // Assert
      expect(onParamsChange).not.toHaveBeenCalled();
    });

    it("clears the filter for an empty term", () => {
      // Arrange
      const { onParamsChange } = renderToolbar({ params: { name: "checkout" } });

      // Act
      submitSearch("");

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: undefined });
    });

    it("clears the filter for a whitespace-only term", () => {
      // Arrange — trimming makes it empty
      const { onParamsChange } = renderToolbar({ params: { name: "checkout" } });

      // Act
      submitSearch("   ");

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: undefined });
    });

    it("trims surrounding whitespace from a submitted term", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("  checkout  ");

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: "checkout" });
    });

    it("measures the minimum length after trimming", () => {
      // Arrange — " ab " trims to 2 characters, below the minimum
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch(" ab ");

      // Assert
      expect(onParamsChange).not.toHaveBeenCalled();
    });

    it("ignores keys other than Enter", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      fireEvent.change(searchBox(), { target: { value: "checkout" } });
      fireEvent.keyDown(searchBox(), { key: "a" });

      // Assert
      expect(onParamsChange).not.toHaveBeenCalled();
    });

    it("ignores the Escape key", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      fireEvent.change(searchBox(), { target: { value: "checkout" } });
      fireEvent.keyDown(searchBox(), { key: "Escape" });

      // Assert
      expect(onParamsChange).not.toHaveBeenCalled();
    });

    it("submits a Turkish search term unchanged", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("ödeme akışı");

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: "ödeme akışı" });
    });

    it("submits a term containing emoji", () => {
      // Arrange
      const { onParamsChange } = renderToolbar();

      // Act
      submitSearch("cart 🛒");

      // Assert
      expect(onParamsChange).toHaveBeenCalledWith({ name: "cart 🛒" });
    });
  });

  describe("status filter", () => {
    it("shows all statuses when no filter is set", () => {
      // Arrange & Act
      renderToolbar({ params: {} });

      // Assert
      expect(screen.getByText("All Status")).toBeInTheDocument();
    });

    it("shows the active filter", () => {
      // Arrange & Act
      renderToolbar({ params: { status: true } });

      // Assert
      expect(screen.getByText("Active")).toBeInTheDocument();
    });

    it("shows the inactive filter", () => {
      // Arrange — status false must not be read as "unset"
      renderToolbar({ params: { status: false } });

      // Act
      const label = screen.getByText("Inactive");

      // Assert
      expect(label).toBeInTheDocument();
    });
  });

  describe("bulk actions", () => {
    it("disables the actions button with nothing selected", () => {
      // Arrange & Act
      renderToolbar({ selectedIds: new Set() });

      // Assert
      expect(actionsButton()).toBeDisabled();
    });

    it("enables the actions button once rows are selected", () => {
      // Arrange & Act
      renderToolbar({ selectedIds: new Set(["a"]) });

      // Assert
      expect(actionsButton()).toBeEnabled();
    });

    it("shows the selected count", () => {
      // Arrange & Act
      renderToolbar({ selectedIds: new Set(["a", "b", "c"]) });

      // Assert
      expect(actionsButton()).toHaveTextContent("Actions (3)");
    });

    it("shows a bare label with nothing selected", () => {
      // Arrange & Act
      renderToolbar({ selectedIds: new Set() });

      // Assert
      expect(actionsButton()).toHaveTextContent("Actions");
    });

    it("reports progress while a bulk action runs", () => {
      // Arrange & Act
      renderToolbar({
        selectedIds: new Set(["a"]),
        isBulkActionPending: true,
      });

      // Assert
      expect(actionsButton()).toHaveTextContent("Processing...");
    });

    it("disables the actions button while a bulk action runs", () => {
      // Arrange & Act
      renderToolbar({
        selectedIds: new Set(["a"]),
        isBulkActionPending: true,
      });

      // Assert
      expect(actionsButton()).toBeDisabled();
    });

    it("activates the selected scenarios", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onBulkStatusChange } = renderToolbar({
        selectedIds: new Set(["a", "b"]),
      });
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Active" }));

      // Assert
      expect(onBulkStatusChange).toHaveBeenCalledWith(["a", "b"], true);
    });

    it("deactivates the selected scenarios", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onBulkStatusChange } = renderToolbar({
        selectedIds: new Set(["a"]),
      });
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Inactive" }));

      // Assert
      expect(onBulkStatusChange).toHaveBeenCalledWith(["a"], false);
    });

    it("deletes the selected scenarios", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onBulkDelete } = renderToolbar({
        selectedIds: new Set(["a", "b"]),
      });
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Delete" }));

      // Assert
      expect(onBulkDelete).toHaveBeenCalledWith(["a", "b"]);
    });

    it("passes the ids in selection order", async () => {
      // Arrange — Set iteration order is insertion order
      const user = userEvent.setup();
      const { onBulkDelete } = renderToolbar({
        selectedIds: new Set(["third", "first", "second"]),
      });
      await user.click(actionsButton());

      // Act
      await user.click(screen.getByRole("menuitem", { name: "Delete" }));

      // Assert
      expect(onBulkDelete).toHaveBeenCalledWith(["third", "first", "second"]);
    });
  });
});
