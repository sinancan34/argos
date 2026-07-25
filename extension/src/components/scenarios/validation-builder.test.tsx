// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm, type UseFormReturn } from "react-hook-form";
import { ValidationBuilder } from "./validation-builder";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

type Validations = ScenarioCreate["validations"];

const GA_VALIDATION = {
  id: "validation-1",
  provider: "google_analytics" as const,
  params: [{ key: "en", match: "exact" as const, value: "page_view" }],
};

const CUSTOM_VALIDATION = {
  id: "validation-2",
  provider: "custom" as const,
  url: { match: "contains" as const, value: "/g/collect" },
  params: [],
};

const EMPTY_VALIDATION = {
  id: "validation-3",
  provider: "" as never,
  params: [],
};

let currentForm: UseFormReturn<ScenarioCreate> | null = null;

function Harness({ validations }: { validations: Validations }) {
  const form = useForm<ScenarioCreate>({
    defaultValues: { validations } as Partial<ScenarioCreate>,
  });
  currentForm = form;
  return <ValidationBuilder form={form} />;
}

function renderBuilder(validations: Validations = [GA_VALIDATION] as Validations) {
  currentForm = null;
  return render(<Harness validations={validations} />);
}

function formValidations(): Validations {
  if (!currentForm) throw new Error("form was not captured");
  return currentForm.getValues("validations");
}

function validationHeaders(): HTMLElement[] {
  return screen.queryAllByRole("button", { name: /VALIDATION \d/ });
}

function providerTrigger(): HTMLElement {
  return screen.getAllByRole("combobox")[0];
}

describe("ValidationBuilder", () => {
  describe("layout", () => {
    it("labels the section", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByText("Validations")).toBeInTheDocument();
    });

    it("offers an add action", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(
        screen.getByRole("button", { name: "+ Add Validation" }),
      ).toBeInTheDocument();
    });

    it("renders one entry per validation", () => {
      // Arrange & Act
      renderBuilder([GA_VALIDATION, CUSTOM_VALIDATION] as Validations);

      // Assert
      expect(validationHeaders()).toHaveLength(2);
    });

    it("numbers the validations from one", () => {
      // Arrange & Act
      renderBuilder([GA_VALIDATION, CUSTOM_VALIDATION] as Validations);

      // Assert
      expect(validationHeaders()[1]).toHaveTextContent("VALIDATION 2");
    });
  });

  describe("adding validations", () => {
    it("appends a validation to the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Validation" }));

      // Assert
      expect(formValidations()).toHaveLength(2);
    });

    it("gives the appended validation no provider yet", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Validation" }));

      // Assert
      expect(formValidations()[1].provider).toBe("");
    });

    it("gives the appended validation no param checks", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Validation" }));

      // Assert
      expect(formValidations()[1].params).toEqual([]);
    });

    it("gives the appended validation a generated id", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(screen.getByRole("button", { name: "+ Add Validation" }));

      // Assert
      expect(formValidations()[1].id).toMatch(/^[0-9a-f-]{36}$/i);
    });
  });

  describe("removing validations", () => {
    it("offers no delete action for a lone validation", () => {
      // Arrange — a scenario needs at least one validation
      renderBuilder([GA_VALIDATION] as Validations);

      // Act
      const deleteButtons = screen.queryAllByRole("button", { name: /Delete/ });

      // Assert
      expect(deleteButtons).toHaveLength(0);
    });

    it("removes the chosen validation", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GA_VALIDATION, CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(screen.getAllByRole("button", { name: /Delete/ })[0]);

      // Assert
      expect(formValidations()).toHaveLength(1);
    });

    it("keeps the validation that was not deleted", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GA_VALIDATION, CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(screen.getAllByRole("button", { name: /Delete/ })[0]);

      // Assert
      expect(formValidations()[0].provider).toBe("custom");
    });
  });

  describe("collapsing", () => {
    it("starts expanded", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByText("Provider")).toBeInTheDocument();
    });

    it("collapses when the header is clicked", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder();

      // Act
      await user.click(validationHeaders()[0]);

      // Assert
      expect(screen.queryByText("Provider")).not.toBeInTheDocument();
    });

    it("summarizes the check count while collapsed", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GA_VALIDATION] as Validations);

      // Act
      await user.click(validationHeaders()[0]);

      // Assert
      expect(validationHeaders()[0]).toHaveTextContent("· 1 check");
    });

    it("pluralizes the check count", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([
        {
          ...GA_VALIDATION,
          params: [
            { key: "en", match: "exact", value: "page_view" },
            { key: "tid", match: "startsWith", value: "G-" },
          ],
        },
      ] as Validations);

      // Act
      await user.click(validationHeaders()[0]);

      // Assert
      expect(validationHeaders()[0]).toHaveTextContent("· 2 checks");
    });

    it("pluralizes a zero check count", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(validationHeaders()[0]);

      // Assert
      expect(validationHeaders()[0]).toHaveTextContent("· 0 checks");
    });
  });

  describe("provider selection", () => {
    it("shows the current provider's display name", () => {
      // Arrange & Act
      renderBuilder([GA_VALIDATION] as Validations);

      // Assert
      expect(providerTrigger()).toHaveTextContent("Google Analytics");
    });

    it("labels the custom provider", () => {
      // Arrange & Act
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Assert
      expect(providerTrigger()).toHaveTextContent("Custom URL");
    });

    it("prompts when no provider is chosen", () => {
      // Arrange & Act
      renderBuilder([EMPTY_VALIDATION] as Validations);

      // Assert
      expect(providerTrigger()).toHaveTextContent("Select provider...");
    });

    it("offers every provider from the shared registry", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([EMPTY_VALIDATION] as Validations);

      // Act
      await user.click(providerTrigger());

      // Assert
      expect(screen.getAllByRole("option")).toHaveLength(2);
    });

    it("writes the chosen provider to the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([EMPTY_VALIDATION] as Validations);
      await user.click(providerTrigger());

      // Act
      await user.click(screen.getByRole("option", { name: "Google Analytics" }));

      // Assert
      expect(formValidations()[0].provider).toBe("google_analytics");
    });

    it("seeds a url check when custom is chosen", async () => {
      // Arrange — a custom provider is invalid without one
      const user = userEvent.setup();
      renderBuilder([EMPTY_VALIDATION] as Validations);
      await user.click(providerTrigger());

      // Act
      await user.click(screen.getByRole("option", { name: "Custom URL" }));

      // Assert
      expect(formValidations()[0].url).toEqual({
        match: "contains",
        value: "",
      });
    });

    it("drops the url check when moving off custom", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);
      await user.click(providerTrigger());

      // Act
      await user.click(screen.getByRole("option", { name: "Google Analytics" }));

      // Assert
      expect(formValidations()[0].url).toBeUndefined();
    });
  });

  describe("url check", () => {
    it("shows the url check for a custom provider", () => {
      // Arrange & Act
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Assert
      expect(screen.getByText("URL Check")).toBeInTheDocument();
    });

    it("hides the url check for a known provider", () => {
      // Arrange & Act
      renderBuilder([GA_VALIDATION] as Validations);

      // Assert
      expect(screen.queryByText("URL Check")).not.toBeInTheDocument();
    });

    it("shows the current url value", () => {
      // Arrange & Act
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Assert
      expect(screen.getByDisplayValue("/g/collect")).toBeInTheDocument();
    });

    it("hides the value input for an exists match", () => {
      // Arrange — nothing to compare against
      renderBuilder([
        { ...CUSTOM_VALIDATION, url: { match: "exists" } },
      ] as unknown as Validations);

      // Assert
      expect(
        screen.queryByPlaceholderText("https://example.com"),
      ).not.toBeInTheDocument();
    });

    it("offers every match type for the url check", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(screen.getAllByRole("combobox")[1]);

      // Assert
      expect(screen.getAllByRole("option")).toHaveLength(6);
    });

    it("writes the chosen url match type to the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);
      await user.click(screen.getAllByRole("combobox")[1]);

      // Act
      await user.click(screen.getByRole("option", { name: "regex" }));

      // Assert
      expect(formValidations()[0].url?.match).toBe("regex");
    });
  });

  describe("parameter checks", () => {
    it("labels the parameter section as optional", () => {
      // Arrange & Act
      renderBuilder();

      // Assert
      expect(screen.getByText("(optional)")).toBeInTheDocument();
    });

    it("appends a parameter check", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(screen.getByRole("button", { name: "+ parameter" }));

      // Assert
      expect(formValidations()[0].params).toHaveLength(1);
    });

    it("defaults a new check to the registry's match type", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(screen.getByRole("button", { name: "+ parameter" }));

      // Assert
      expect(formValidations()[0].params[0].match).toBe("exact");
    });

    it("defaults a new check to an empty key", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION] as Validations);

      // Act
      await user.click(screen.getByRole("button", { name: "+ parameter" }));

      // Assert
      expect(formValidations()[0].params[0].key).toBe("");
    });

    it("shows the current param value", () => {
      // Arrange & Act
      renderBuilder([GA_VALIDATION] as Validations);

      // Assert
      expect(screen.getByDisplayValue("page_view")).toBeInTheDocument();
    });

    it("removes a parameter check", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([GA_VALIDATION] as Validations);

      // Act
      await user.click(screen.getByRole("button", { name: "×" }));

      // Assert
      expect(formValidations()[0].params).toHaveLength(0);
    });

    it("uses a plain key input when the provider has no suggestions", () => {
      // Arrange — custom carries no paramSuggestions
      renderBuilder([
        { ...CUSTOM_VALIDATION, params: [{ key: "utm", match: "exact", value: "x" }] },
      ] as Validations);

      // Assert
      expect(screen.getByPlaceholderText("key")).toBeInTheDocument();
    });

    it("hides the value input for an exists match", () => {
      // Arrange
      renderBuilder([
        { ...CUSTOM_VALIDATION, params: [{ key: "utm", match: "exists" }] },
      ] as unknown as Validations);

      // Assert
      expect(
        screen.queryByPlaceholderText("expected value"),
      ).not.toBeInTheDocument();
    });

    it("writes the chosen param match type to the form state", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([
        { ...CUSTOM_VALIDATION, params: [{ key: "utm", match: "exact", value: "x" }] },
      ] as Validations);
      const matchTrigger = screen.getAllByRole("combobox").at(-1) as HTMLElement;
      await user.click(matchTrigger);

      // Act
      await user.click(screen.getByRole("option", { name: "contains" }));

      // Assert
      expect(formValidations()[0].params[0].match).toBe("contains");
    });

    it("keeps two validations' parameter lists independent", async () => {
      // Arrange
      const user = userEvent.setup();
      renderBuilder([CUSTOM_VALIDATION, GA_VALIDATION] as Validations);

      // Act
      await user.click(
        screen.getAllByRole("button", { name: "+ parameter" })[0],
      );

      // Assert
      expect(formValidations()[1].params).toHaveLength(1);
    });
  });
});
