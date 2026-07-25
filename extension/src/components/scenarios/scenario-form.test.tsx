// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ScenarioResponse } from "../../lib/schemas/scenario";

const { navigateMock } = vi.hoisted(() => ({ navigateMock: vi.fn() }));

vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => navigateMock,
}));

vi.mock("./device-select", () => ({
  DeviceSelect: ({
    value,
    onChange,
    hasError,
  }: {
    value: string;
    onChange: (id: string) => void;
    hasError?: boolean;
  }) => (
    <input
      data-testid="device-select"
      aria-invalid={hasError || undefined}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

vi.mock("./selector-field", () => ({
  SelectorField: ({ value }: { value: string }) => (
    <input data-testid="selector-field" defaultValue={value} />
  ),
}));

import { ScenarioForm } from "./scenario-form";

const DEVICE_ID = "5b1f0d2e-0000-4000-8000-000000000000";
const DEFAULT_STEP_TIMEOUT = 5000;
const DEFAULT_VALIDATION_TIMEOUT = 10000;

const EXISTING: ScenarioResponse = {
  id: "scenario-1",
  name: "Checkout flow",
  description: "Validates the GA4 page_view",
  status: true,
  device_id: DEVICE_ID,
  step_timeout: 3000,
  validation_timeout: 8000,
  steps: [
    { id: "step-1", command: "goto", params: { url: "https://example.com" } },
  ],
  validations: [
    { id: "validation-1", provider: "google_analytics", params: [] },
  ],
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
} as unknown as ScenarioResponse;

interface RenderOptions {
  mode?: "create" | "edit";
  defaultValues?: ScenarioResponse;
  isSubmitting?: boolean;
}

function renderForm({
  mode = "create",
  defaultValues,
  isSubmitting = false,
}: RenderOptions = {}) {
  const onSubmit = vi.fn();
  const view = render(
    <ScenarioForm
      mode={mode}
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
    />,
  );
  return { ...view, onSubmit };
}

function nameInput(): HTMLElement {
  return screen.getByLabelText(/Name/);
}

function submitButton(): HTMLElement {
  return screen.getByRole("button", {
    name: /Create Scenario|Save Changes|Saving/,
  });
}

/** The payload passed to onSubmit on the latest call. */
function submitted(onSubmit: ReturnType<typeof vi.fn>): Record<string, unknown> {
  const call = onSubmit.mock.calls.at(-1);
  if (!call) throw new Error("onSubmit was not called");
  return call[0] as Record<string, unknown>;
}

describe("ScenarioForm", () => {
  beforeEach(() => {
    navigateMock.mockReset();
  });

  describe("create mode", () => {
    it("starts with an empty name", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(nameInput()).toHaveValue("");
    });

    it("seeds the step timeout from the shared registry default", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(screen.getByLabelText("Step Timeout (ms)")).toHaveValue(
        DEFAULT_STEP_TIMEOUT,
      );
    });

    it("seeds the validation timeout from the shared registry default", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(screen.getByLabelText("Validation Timeout (ms)")).toHaveValue(
        DEFAULT_VALIDATION_TIMEOUT,
      );
    });

    it("starts with one empty step", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(
        screen.getByRole("button", { name: /STEP 1/ }),
      ).toBeInTheDocument();
    });

    it("starts with one empty validation", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(
        screen.getByRole("button", { name: /VALIDATION 1/ }),
      ).toBeInTheDocument();
    });

    it("labels the submit action for creation", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(submitButton()).toHaveTextContent("Create Scenario");
    });

    it("submits the whole payload when valid", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onSubmit } = renderForm();
      fireEvent.change(nameInput(), { target: { value: "Checkout flow" } });
      fireEvent.change(screen.getByTestId("device-select"), {
        target: { value: DEVICE_ID },
      });
      // Two selects are on screen: the step's command, then the validation's provider.
      await user.click(screen.getAllByRole("combobox")[0]);
      await user.click(screen.getByRole("option", { name: "goto" }));
      await user.click(screen.getAllByRole("combobox")[1]);
      await user.click(screen.getByRole("option", { name: "Google Analytics" }));

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() =>
        expect(submitted(onSubmit)).toMatchObject({
          name: "Checkout flow",
          device_id: DEVICE_ID,
        }),
      );
    });

    it("blocks submission when the name is missing", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onSubmit } = renderForm();

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() => expect(onSubmit).not.toHaveBeenCalled());
    });

    it("reports the validation errors after a blocked submission", async () => {
      // Arrange
      const user = userEvent.setup();
      renderForm();

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() =>
        expect(
          screen.getByText(
            "Please fix the validation errors above before saving.",
          ),
        ).toBeInTheDocument(),
      );
    });

    it("marks the device field invalid when it is missing", async () => {
      // Arrange
      const user = userEvent.setup();
      renderForm();

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() =>
        expect(screen.getByTestId("device-select")).toHaveAttribute(
          "aria-invalid",
          "true",
        ),
      );
    });
  });

  describe("edit mode", () => {
    it("prefills the name", () => {
      // Arrange & Act
      renderForm({ mode: "edit", defaultValues: EXISTING });

      // Assert
      expect(nameInput()).toHaveValue("Checkout flow");
    });

    it("prefills the description", () => {
      // Arrange & Act
      renderForm({ mode: "edit", defaultValues: EXISTING });

      // Assert
      expect(screen.getByLabelText("Description")).toHaveValue(
        "Validates the GA4 page_view",
      );
    });

    it("prefills the timeouts from the scenario", () => {
      // Arrange & Act
      renderForm({ mode: "edit", defaultValues: EXISTING });

      // Assert
      expect(screen.getByLabelText("Step Timeout (ms)")).toHaveValue(3000);
    });

    it("prefills the device", () => {
      // Arrange & Act
      renderForm({ mode: "edit", defaultValues: EXISTING });

      // Assert
      expect(screen.getByTestId("device-select")).toHaveValue(DEVICE_ID);
    });

    it("renders an empty description for a null one", () => {
      // Arrange & Act
      renderForm({
        mode: "edit",
        defaultValues: { ...EXISTING, description: null } as ScenarioResponse,
      });

      // Assert
      expect(screen.getByLabelText("Description")).toHaveValue("");
    });

    it("labels the submit action for saving", () => {
      // Arrange & Act
      renderForm({ mode: "edit", defaultValues: EXISTING });

      // Assert
      expect(submitButton()).toHaveTextContent("Save Changes");
    });

    it("sends only the changed field", async () => {
      // Arrange — an edit submits a sparse patch, not the whole record
      const user = userEvent.setup();
      const { onSubmit } = renderForm({
        mode: "edit",
        defaultValues: EXISTING,
      });
      fireEvent.change(nameInput(), { target: { value: "Renamed flow" } });

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() =>
        expect(submitted(onSubmit)).toEqual({ name: "Renamed flow" }),
      );
    });

    it("omits untouched fields from the patch", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onSubmit } = renderForm({
        mode: "edit",
        defaultValues: EXISTING,
      });
      fireEvent.change(nameInput(), { target: { value: "Renamed flow" } });

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() =>
        expect(submitted(onSubmit)).not.toHaveProperty("device_id"),
      );
    });

    it("blocks submission while an added step has no command", async () => {
      // Arrange — a freshly appended step starts with an empty command
      const user = userEvent.setup();
      const { onSubmit } = renderForm({
        mode: "edit",
        defaultValues: EXISTING,
      });
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() => expect(onSubmit).not.toHaveBeenCalled());
    });

    it("includes the steps in the patch when a step's command changes", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onSubmit } = renderForm({
        mode: "edit",
        defaultValues: EXISTING,
      });
      await user.click(screen.getAllByRole("combobox")[0]);
      await user.click(screen.getByRole("option", { name: "click" }));

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() => expect(submitted(onSubmit)).toHaveProperty("steps"));
    });

    it("sends an empty patch when nothing was touched", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onSubmit } = renderForm({
        mode: "edit",
        defaultValues: EXISTING,
      });

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() => expect(submitted(onSubmit)).toEqual({}));
    });

    it("accepts an empty name patch field only through validation", async () => {
      // Arrange — the update schema still enforces the minimum length
      const user = userEvent.setup();
      const { onSubmit } = renderForm({
        mode: "edit",
        defaultValues: EXISTING,
      });
      fireEvent.change(nameInput(), { target: { value: "" } });

      // Act
      await user.click(submitButton());

      // Assert
      await waitFor(() => expect(onSubmit).not.toHaveBeenCalled());
    });
  });

  describe("submission state", () => {
    it("reports progress while submitting", () => {
      // Arrange & Act
      renderForm({ isSubmitting: true });

      // Assert
      expect(submitButton()).toHaveTextContent("Saving...");
    });

    it("disables the submit button while submitting", () => {
      // Arrange & Act
      renderForm({ isSubmitting: true });

      // Assert
      expect(submitButton()).toBeDisabled();
    });

    it("enables the submit button when idle", () => {
      // Arrange & Act
      renderForm();

      // Assert
      expect(submitButton()).toBeEnabled();
    });
  });

  describe("cancelling", () => {
    it("returns to the list", async () => {
      // Arrange
      const user = userEvent.setup();
      renderForm();

      // Act
      await user.click(screen.getByRole("button", { name: "Cancel" }));

      // Assert
      expect(navigateMock).toHaveBeenCalledWith({ to: "/" });
    });

    it("does not submit when cancelling", async () => {
      // Arrange
      const user = userEvent.setup();
      const { onSubmit } = renderForm();

      // Act
      await user.click(screen.getByRole("button", { name: "Cancel" }));

      // Assert
      expect(onSubmit).not.toHaveBeenCalled();
    });
  });
});
