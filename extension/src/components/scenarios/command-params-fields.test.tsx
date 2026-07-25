// @vitest-environment jsdom

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm, type UseFormReturn } from "react-hook-form";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

vi.mock("./selector-field", () => ({
  SelectorField: ({
    value,
    onChange,
  }: {
    value: string;
    onChange: (v: string) => void;
  }) => (
    <input
      data-testid="selector-field"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

// A command carrying an int param. shared/commands.json has none today, so the
// numeric branch is only reachable with an injected registry.
const INT_COMMAND = {
  command: "wait",
  category: "Timing",
  params: [
    {
      name: "duration",
      type: "int" as const,
      required: true,
      placeholder: "1000",
    },
  ],
};

const { commandMapOverride } = vi.hoisted(() => ({
  commandMapOverride: { current: null as Map<string, unknown> | null },
}));

vi.mock("../../lib/commands", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/commands")>();
  return {
    ...actual,
    get COMMAND_MAP() {
      return commandMapOverride.current ?? actual.COMMAND_MAP;
    },
  };
});

import { CommandParamsFields } from "./command-params-fields";

type Steps = ScenarioCreate["steps"];

let currentForm: UseFormReturn<ScenarioCreate> | null = null;

function Harness({ steps }: { steps: Steps }) {
  const form = useForm<ScenarioCreate>({
    defaultValues: { steps } as Partial<ScenarioCreate>,
  });
  currentForm = form;
  return <CommandParamsFields form={form} stepIndex={0} />;
}

function renderFields(steps: Steps) {
  currentForm = null;
  return render(<Harness steps={steps} />);
}

function stepParams(): Record<string, unknown> {
  if (!currentForm) throw new Error("form was not captured");
  return currentForm.getValues("steps")[0].params as Record<string, unknown>;
}

function makeStep(
  command: string,
  params: Record<string, unknown> = {},
): Steps {
  return [{ id: "step-1", command, params }] as Steps;
}

describe("CommandParamsFields", () => {
  describe("string params", () => {
    it("labels the param by name", () => {
      // Arrange & Act
      renderFields(makeStep("goto", { url: "https://example.com" }));

      // Assert
      expect(screen.getByText("url")).toBeInTheDocument();
    });

    it("marks a required param", () => {
      // Arrange & Act
      renderFields(makeStep("goto", { url: "" }));

      // Assert
      expect(screen.getByText("*")).toBeInTheDocument();
    });

    it("shows the current value", () => {
      // Arrange & Act
      renderFields(makeStep("goto", { url: "https://example.com" }));

      // Assert
      expect(screen.getByRole("textbox")).toHaveValue("https://example.com");
    });

    it("renders an empty input for a missing param", () => {
      // Arrange & Act
      renderFields(makeStep("goto", {}));

      // Assert
      expect(screen.getByRole("textbox")).toHaveValue("");
    });

    it("shows the registry placeholder", () => {
      // Arrange & Act
      renderFields(makeStep("goto", {}));

      // Assert
      expect(
        screen.getByPlaceholderText("https://example.com"),
      ).toBeInTheDocument();
    });

    it("writes typed text to the form state", () => {
      // Arrange
      renderFields(makeStep("goto", {}));

      // Act
      fireEvent.change(screen.getByRole("textbox"), {
        target: { value: "https://argos.test" },
      });

      // Assert
      expect(stepParams().url).toBe("https://argos.test");
    });

    it("writes an empty string when the input is cleared", () => {
      // Arrange
      renderFields(makeStep("goto", { url: "https://example.com" }));

      // Act
      fireEvent.change(screen.getByRole("textbox"), { target: { value: "" } });

      // Assert
      expect(stepParams().url).toBe("");
    });

    it("preserves unrelated params when one changes", () => {
      // Arrange — params is a free-form record, so extras must survive
      renderFields(makeStep("goto", { url: "", extra: "keep me" }));

      // Act
      fireEvent.change(screen.getByRole("textbox"), {
        target: { value: "https://argos.test" },
      });

      // Assert
      expect(stepParams().extra).toBe("keep me");
    });

    it("accepts a Turkish value", () => {
      // Arrange
      renderFields(makeStep("goto", {}));

      // Act
      fireEvent.change(screen.getByRole("textbox"), {
        target: { value: "https://örnek.test/ödeme" },
      });

      // Assert
      expect(stepParams().url).toBe("https://örnek.test/ödeme");
    });
  });

  describe("selector param", () => {
    it("renders the picker-backed field for a click step", () => {
      // Arrange & Act
      renderFields(makeStep("click", { selector: "#buy" }));

      // Assert
      expect(screen.getByTestId("selector-field")).toBeInTheDocument();
    });

    it("passes the current selector to the field", () => {
      // Arrange & Act
      renderFields(makeStep("click", { selector: "#buy" }));

      // Assert
      expect(screen.getByTestId("selector-field")).toHaveValue("#buy");
    });

    it("passes an empty string when the selector is absent", () => {
      // Arrange & Act
      renderFields(makeStep("click", {}));

      // Assert
      expect(screen.getByTestId("selector-field")).toHaveValue("");
    });

    it("writes the selector back to the form state", () => {
      // Arrange
      renderFields(makeStep("click", { selector: "" }));

      // Act
      fireEvent.change(screen.getByTestId("selector-field"), {
        target: { value: "button.primary" },
      });

      // Assert
      expect(stepParams().selector).toBe("button.primary");
    });

    it("renders no plain label for the selector param", () => {
      // Arrange — SelectorField supplies its own label
      renderFields(makeStep("click", { selector: "#buy" }));

      // Assert
      expect(screen.queryByText("selector")).not.toBeInTheDocument();
    });
  });

  describe("unknown or param-less commands", () => {
    it("renders nothing for an unknown command", () => {
      // Arrange & Act
      const { container } = renderFields(makeStep("scroll", {}));

      // Assert
      expect(container).toBeEmptyDOMElement();
    });

    it("renders nothing for an empty command", () => {
      // Arrange & Act
      const { container } = renderFields(makeStep("", {}));

      // Assert
      expect(container).toBeEmptyDOMElement();
    });
  });

  describe("resetting params on a command change", () => {
    it("keeps the initial params on first render", () => {
      // Arrange — the reset must not fire on mount
      renderFields(makeStep("goto", { url: "https://example.com" }));

      // Act
      const params = stepParams();

      // Assert
      expect(params.url).toBe("https://example.com");
    });

    it("clears stale params when the command changes", async () => {
      // Arrange
      renderFields(makeStep("goto", { url: "https://example.com" }));

      // Act
      await vi.waitFor(() => {
        currentForm?.setValue("steps.0.command", "click");
      });

      // Assert
      await vi.waitFor(() => expect(stepParams().url).toBeUndefined());
    });

    it("seeds the new command's params with empty strings", async () => {
      // Arrange
      renderFields(makeStep("goto", { url: "https://example.com" }));

      // Act
      await vi.waitFor(() => {
        currentForm?.setValue("steps.0.command", "click");
      });

      // Assert
      await vi.waitFor(() => expect(stepParams().selector).toBe(""));
    });
  });

  describe("integer params", () => {
    it("renders a number input", async () => {
      // Arrange
      commandMapOverride.current = new Map([[INT_COMMAND.command, INT_COMMAND]]);

      // Act
      renderFields(makeStep("wait", { duration: 1000 }));

      // Assert
      expect(screen.getByRole("spinbutton")).toBeInTheDocument();
      commandMapOverride.current = null;
    });

    it("shows the current numeric value", () => {
      // Arrange
      commandMapOverride.current = new Map([[INT_COMMAND.command, INT_COMMAND]]);

      // Act
      renderFields(makeStep("wait", { duration: 1000 }));

      // Assert
      expect(screen.getByRole("spinbutton")).toHaveValue(1000);
      commandMapOverride.current = null;
    });

    it("renders zero rather than treating it as absent", () => {
      // Arrange — a truthiness check would blank this out
      commandMapOverride.current = new Map([[INT_COMMAND.command, INT_COMMAND]]);

      // Act
      renderFields(makeStep("wait", { duration: 0 }));

      // Assert
      expect(screen.getByRole("spinbutton")).toHaveValue(0);
      commandMapOverride.current = null;
    });

    it("stores a typed number as a number", () => {
      // Arrange
      commandMapOverride.current = new Map([[INT_COMMAND.command, INT_COMMAND]]);
      renderFields(makeStep("wait", {}));

      // Act
      fireEvent.change(screen.getByRole("spinbutton"), {
        target: { value: "250" },
      });

      // Assert
      expect(stepParams().duration).toBe(250);
      commandMapOverride.current = null;
    });

    it("stores undefined when the number input is cleared", () => {
      // Arrange
      commandMapOverride.current = new Map([[INT_COMMAND.command, INT_COMMAND]]);
      renderFields(makeStep("wait", { duration: 1000 }));

      // Act
      fireEvent.change(screen.getByRole("spinbutton"), {
        target: { value: "" },
      });

      // Assert
      expect(stepParams().duration).toBeUndefined();
      commandMapOverride.current = null;
    });

    it("renders an empty input for an absent numeric param", () => {
      // Arrange
      commandMapOverride.current = new Map([[INT_COMMAND.command, INT_COMMAND]]);

      // Act
      renderFields(makeStep("wait", {}));

      // Assert
      expect(screen.getByRole("spinbutton")).toHaveValue(null);
      commandMapOverride.current = null;
    });
  });
});
