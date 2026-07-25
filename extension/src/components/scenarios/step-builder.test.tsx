// @vitest-environment jsdom

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm, type UseFormReturn } from "react-hook-form";
import { StepBuilder } from "./step-builder";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

vi.mock("./selector-field", () => ({
  SelectorField: ({ value }: { value: string }) => (
    <input data-testid="selector-field" defaultValue={value} />
  ),
}));

const GOTO_STEP = {
  id: "step-1",
  command: "goto" as const,
  params: { url: "https://example.com" },
};
const CLICK_STEP = {
  id: "step-2",
  command: "click" as const,
  params: { selector: "#buy" },
};

type Steps = ScenarioCreate["steps"];

let currentForm: UseFormReturn<ScenarioCreate> | null = null;

interface HarnessProps {
  steps: Steps;
}

function Harness({ steps }: HarnessProps) {
  const form = useForm<ScenarioCreate>({
    defaultValues: { steps } as Partial<ScenarioCreate>,
  });
  currentForm = form;
  return <StepBuilder form={form} />;
}

function renderBuilder(steps: Steps = [GOTO_STEP] as Steps) {
  currentForm = null;
  return render(<Harness steps={steps} />);
}

/** The steps currently held in the form state. */
function formSteps(): Steps {
  if (!currentForm) throw new Error("form was not captured");
  return currentForm.getValues("steps");
}

/** Collapsible headers, one per step. Uses queryAll so an empty list yields []. */
function stepHeaders(): HTMLElement[] {
  return screen.queryAllByRole("button", { name: /STEP \d/ });
}

describe("StepBuilder", () => {
  describe("layout", () => {
    it("labels the section", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByText("Steps")).toBeInTheDocument();
    });

    it("offers an add action", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(
        screen.getByRole("button", { name: "+ Add Step" }),
      ).toBeInTheDocument();
    });

    it("renders one entry per step", () => {
      // Arrange & Act
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Assert
      expect(stepHeaders()).toHaveLength(2);
    });

    it("numbers the steps from one", () => {
      // Arrange & Act
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Assert
      expect(stepHeaders()[1]).toHaveTextContent("STEP 2");
    });

    it("renders nothing but the header for an empty step list", () => {
      // Arrange & Act
      renderBuilder([] as unknown as Steps);

      // Assert
      expect(stepHeaders()).toHaveLength(0);
    });

    it("keeps the add button out of form submission", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByRole("button", { name: "+ Add Step" })).toHaveAttribute(
        "type",
        "button",
      );
    });
  });

  describe("adding steps", () => {
    it("appends a step to the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Assert
      expect(formSteps()).toHaveLength(2);
    });

    it("renders the appended step", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Assert
      expect(stepHeaders()).toHaveLength(2);
    });

    it("gives the appended step no command yet", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Assert
      expect(formSteps()[1].command).toBe("");
    });

    it("gives the appended step empty params", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Assert
      expect(formSteps()[1].params).toEqual({});
    });

    it("gives the appended step a generated id", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Assert
      expect(formSteps()[1].id).toMatch(/^[0-9a-f-]{36}$/i);
    });

    it("gives each appended step a distinct id", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));
      await user.click(screen.getByRole("button", { name: "+ Add Step" }));

      // Assert
      expect(formSteps()[1].id).not.toBe(formSteps()[2].id);
    });
  });

  describe("removing steps", () => {
    it("offers no delete action for a lone step", () => {
      // Arrange — a scenario needs at least one step
      renderBuilder([GOTO_STEP] as Steps);

      // Act
      const deleteButtons = screen.queryAllByRole("button", { name: /Delete/ });

      // Assert
      expect(deleteButtons).toHaveLength(0);
    });

    it("offers a delete action per step when several exist", () => {
      // Arrange & Act
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Assert
      expect(screen.getAllByRole("button", { name: /Delete/ })).toHaveLength(2);
    });

    it("removes the chosen step from the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Act
      await user.click(screen.getAllByRole("button", { name: /Delete/ })[0]);

      // Assert
      expect(formSteps()).toHaveLength(1);
    });

    it("keeps the step that was not deleted", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Act
      await user.click(screen.getAllByRole("button", { name: /Delete/ })[0]);

      // Assert
      expect(formSteps()[0].command).toBe("click");
    });

    it("hides the delete action once one step remains", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Act
      await user.click(screen.getAllByRole("button", { name: /Delete/ })[0]);

      // Assert
      expect(screen.queryAllByRole("button", { name: /Delete/ })).toHaveLength(0);
    });

    it("renumbers the remaining steps", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Act
      await user.click(screen.getAllByRole("button", { name: /Delete/ })[0]);

      // Assert
      expect(stepHeaders()[0]).toHaveTextContent("STEP 1");
    });
  });

  describe("collapsing", () => {
    it("starts expanded", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByText("Command")).toBeInTheDocument();
    });

    it("collapses when the header is clicked", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(stepHeaders()[0]);

      // Assert
      expect(screen.queryByText("Command")).not.toBeInTheDocument();
    });

    it("summarizes the command while collapsed", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(stepHeaders()[0]);

      // Assert
      expect(stepHeaders()[0]).toHaveTextContent("· goto");
    });

    it("omits the summary for a step with no command", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([{ id: "s1", command: "" as never, params: {} }] as Steps);

      // Act
      await user.click(stepHeaders()[0]);

      // Assert
      expect(stepHeaders()[0]).not.toHaveTextContent("·");
    });

    it("expands again on a second click", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();
      await user.click(stepHeaders()[0]);

      // Act
      await user.click(stepHeaders()[0]);

      // Assert
      expect(screen.getByText("Command")).toBeInTheDocument();
    });

    it("collapses only the step that was clicked", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GOTO_STEP, CLICK_STEP] as Steps);

      // Act
      await user.click(stepHeaders()[0]);

      // Assert
      expect(screen.getAllByText("Command")).toHaveLength(1);
    });
  });

  describe("command selection", () => {
    it("shows the step's current command", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByRole("combobox")).toHaveTextContent("goto");
    });

    it("prompts for a command when none is set", () => {
      // Arrange & Act
      renderBuilder([{ id: "s1", command: "" as never, params: {} }] as Steps);

      // Assert
      expect(screen.getByRole("combobox")).toHaveTextContent(
        "Select command...",
      );
    });

    it("groups the options by category", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("combobox"));

      // Assert
      expect(screen.getByText("Navigation")).toBeInTheDocument();
    });

    it("writes the chosen command to the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();
      await user.click(screen.getByRole("combobox"));

      // Act
      await user.click(screen.getByRole("option", { name: "click" }));

      // Assert
      expect(formSteps()[0].command).toBe("click");
    });

    it("offers every command from the shared registry", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("combobox"));

      // Assert
      expect(screen.getAllByRole("option")).toHaveLength(2);
    });
  });

  describe("command params", () => {
    it("renders the url field for a goto step", () => {
      // Arrange & Act
      renderBuilder([GOTO_STEP] as Steps);

      // Assert
      expect(screen.getByText("url")).toBeInTheDocument();
    });

    it("shows the current url value", () => {
      // Arrange & Act
      renderBuilder([GOTO_STEP] as Steps);

      // Assert
      expect(
        screen.getByDisplayValue("https://example.com"),
      ).toBeInTheDocument();
    });

    it("renders the picker-backed selector field for a click step", () => {
      // Arrange & Act
      renderBuilder([CLICK_STEP] as Steps);

      // Assert
      expect(screen.getByTestId("selector-field")).toBeInTheDocument();
    });

    it("renders no param fields for a step with no command", () => {
      // Arrange & Act
      renderBuilder([{ id: "s1", command: "" as never, params: {} }] as Steps);

      // Assert
      expect(screen.queryByText("url")).not.toBeInTheDocument();
    });
  });
});
