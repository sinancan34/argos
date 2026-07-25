// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { PickerSelectorResult } from "../../lib/picker/types";

const { useElementPickerMock, startPickerMock, cancelPickerMock } = vi.hoisted(
  () => ({
    useElementPickerMock: vi.fn(),
    startPickerMock: vi.fn(),
    cancelPickerMock: vi.fn(),
  }),
);

vi.mock("../../lib/hooks/use-element-picker", () => ({
  useElementPicker: () => useElementPickerMock(),
}));

import { SelectorField } from "./selector-field";

const SELECTOR = "div.product-card > button";

/** Configures the mocked hook's picking state. */
function primePicker(isPicking = false): void {
  useElementPickerMock.mockReturnValue({
    isPicking,
    startPicker: startPickerMock,
    cancelPicker: cancelPickerMock,
  });
}

/** Invokes the callback the component handed to startPicker. */
function emitPickResult(result: PickerSelectorResult): void {
  const call = startPickerMock.mock.calls.at(-1);
  if (!call) throw new Error("startPicker was not called");
  const onResult = call[0] as (r: PickerSelectorResult) => void;
  act(() => onResult(result));
}

function pickButton(): HTMLElement {
  return screen.getByRole("button", {
    name: /pick element from page|cancel picker/i,
  });
}

describe("SelectorField", () => {
  beforeEach(() => {
    useElementPickerMock.mockReset();
    startPickerMock.mockReset();
    cancelPickerMock.mockReset();
    primePicker(false);
  });

  it("renders the selector label", () => {
    // Arrange & Act
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Assert
    expect(screen.getByText("Selector")).toBeInTheDocument();
  });

  it("shows the current value in the input", () => {
    // Arrange & Act
    render(<SelectorField value={SELECTOR} onChange={vi.fn()} />);

    // Assert
    expect(screen.getByRole("textbox")).toHaveValue(SELECTOR);
  });

  it("renders an empty input for an empty value", () => {
    // Arrange & Act
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Assert
    expect(screen.getByRole("textbox")).toHaveValue("");
  });

  it("shows a placeholder hint", () => {
    // Arrange & Act
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Assert
    expect(screen.getByPlaceholderText("div.my-class")).toBeInTheDocument();
  });

  it("reports each typed character through onChange", async () => {
    // Arrange
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={onChange} />);

    // Act
    await user.type(screen.getByRole("textbox"), "a");

    // Assert
    expect(onChange).toHaveBeenCalledWith("a");
  });

  it("reports a cleared input as an empty string", async () => {
    // Arrange
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<SelectorField value="#a" onChange={onChange} />);

    // Act
    await user.clear(screen.getByRole("textbox"));

    // Assert
    expect(onChange).toHaveBeenCalledWith("");
  });

  it("labels the pick button for starting when idle", () => {
    // Arrange & Act
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Assert
    expect(pickButton()).toHaveAttribute("title", "Pick element from page");
  });

  it("labels the pick button for cancelling while picking", () => {
    // Arrange
    primePicker(true);

    // Act
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Assert
    expect(pickButton()).toHaveAttribute("title", "Cancel picker");
  });

  it("starts the picker when the button is clicked while idle", async () => {
    // Arrange
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Act
    await user.click(pickButton());

    // Assert
    expect(startPickerMock).toHaveBeenCalledTimes(1);
  });

  it("cancels the picker when the button is clicked while picking", async () => {
    // Arrange
    primePicker(true);
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Act
    await user.click(pickButton());

    // Assert
    expect(cancelPickerMock).toHaveBeenCalledTimes(1);
  });

  it("does not start the picker again while one is active", async () => {
    // Arrange
    primePicker(true);
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Act
    await user.click(pickButton());

    // Assert
    expect(startPickerMock).not.toHaveBeenCalled();
  });

  it("applies the picked primary selector", async () => {
    // Arrange
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={onChange} />);
    await user.click(pickButton());

    // Act
    emitPickResult({ primary: SELECTOR, alternatives: [] });

    // Assert
    expect(onChange).toHaveBeenCalledWith(SELECTOR);
  });

  it("renders no alternative chips when none were returned", async () => {
    // Arrange
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);
    await user.click(pickButton());

    // Act
    emitPickResult({ primary: SELECTOR, alternatives: [] });

    // Assert
    expect(screen.getAllByRole("button")).toHaveLength(1);
  });

  it("renders a chip per returned alternative", async () => {
    // Arrange
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);
    await user.click(pickButton());

    // Act
    emitPickResult({
      primary: SELECTOR,
      alternatives: ["#alt-one", ".alt-two"],
    });

    // Assert
    expect(screen.getByRole("button", { name: "#alt-one" })).toBeInTheDocument();
  });

  it("applies an alternative when its chip is clicked", async () => {
    // Arrange
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={onChange} />);
    await user.click(pickButton());
    emitPickResult({ primary: SELECTOR, alternatives: ["#alt-one"] });

    // Act
    await user.click(screen.getByRole("button", { name: "#alt-one" }));

    // Assert
    expect(onChange).toHaveBeenLastCalledWith("#alt-one");
  });

  it("clears the chips once an alternative is chosen", async () => {
    // Arrange
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);
    await user.click(pickButton());
    emitPickResult({ primary: SELECTOR, alternatives: ["#alt-one"] });

    // Act
    await user.click(screen.getByRole("button", { name: "#alt-one" }));

    // Assert
    expect(
      screen.queryByRole("button", { name: "#alt-one" }),
    ).not.toBeInTheDocument();
  });

  it("clears previous alternatives when a new pick starts", async () => {
    // Arrange
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);
    await user.click(pickButton());
    emitPickResult({ primary: SELECTOR, alternatives: ["#stale"] });

    // Act
    await user.click(pickButton());

    // Assert
    expect(screen.queryByRole("button", { name: "#stale" })).not.toBeInTheDocument();
  });

  it("titles each chip with its full selector", async () => {
    // Arrange — chips truncate visually, so the title carries the full text
    const longAlternative = "body > div:nth-child(3) > section > button.primary";
    const user = userEvent.setup();
    render(<SelectorField value="" onChange={vi.fn()} />);
    await user.click(pickButton());

    // Act
    emitPickResult({ primary: SELECTOR, alternatives: [longAlternative] });

    // Assert
    expect(
      screen.getByRole("button", { name: longAlternative }),
    ).toHaveAttribute("title", longAlternative);
  });

  it("keeps the pick button out of form submission", () => {
    // Arrange — the field renders inside the scenario form

    // Act
    render(<SelectorField value="" onChange={vi.fn()} />);

    // Assert
    expect(pickButton()).toHaveAttribute("type", "button");
  });
});
