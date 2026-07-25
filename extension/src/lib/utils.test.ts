import { describe, it, expect } from "vitest";
import { cn } from "./utils";

const LONG_CLASS_REPEAT = 2000;

describe("cn", () => {
  it("joins two class strings", () => {
    // Arrange
    const base = "px-2";
    const extra = "text-sm";

    // Act
    const result = cn(base, extra);

    // Assert
    expect(result).toBe("px-2 text-sm");
  });

  it("returns an empty string with no arguments", () => {
    // Arrange — no inputs at all

    // Act
    const result = cn();

    // Assert
    expect(result).toBe("");
  });

  it("lets a later Tailwind class win over an earlier conflicting one", () => {
    // Arrange — both set padding-x, so tailwind-merge keeps the last

    // Act
    const result = cn("px-2", "px-4");

    // Assert
    expect(result).toBe("px-4");
  });

  it("keeps non-conflicting Tailwind classes side by side", () => {
    // Arrange — padding-x and padding-y do not conflict

    // Act
    const result = cn("px-2", "py-4");

    // Assert
    expect(result).toBe("px-2 py-4");
  });

  it("resolves a conflict across a responsive variant boundary", () => {
    // Arrange — sm:px-4 and px-2 target different breakpoints

    // Act
    const result = cn("px-2", "sm:px-4");

    // Assert
    expect(result).toBe("px-2 sm:px-4");
  });

  it("drops a false conditional class", () => {
    // Arrange
    const isActive = false;

    // Act
    const result = cn("px-2", isActive && "bg-blue-500");

    // Assert
    expect(result).toBe("px-2");
  });

  it("keeps a true conditional class", () => {
    // Arrange
    const isActive = true;

    // Act
    const result = cn("px-2", isActive && "bg-blue-500");

    // Assert
    expect(result).toBe("px-2 bg-blue-500");
  });

  it("ignores null", () => {
    // Arrange — null is a valid ClassValue that contributes nothing

    // Act
    const result = cn("px-2", null);

    // Assert
    expect(result).toBe("px-2");
  });

  it("ignores undefined", () => {
    // Arrange — undefined is a valid ClassValue that contributes nothing

    // Act
    const result = cn("px-2", undefined);

    // Assert
    expect(result).toBe("px-2");
  });

  it("ignores an empty string", () => {
    // Arrange — an empty segment must not introduce stray whitespace

    // Act
    const result = cn("px-2", "");

    // Assert
    expect(result).toBe("px-2");
  });

  it("ignores zero because it is falsy", () => {
    // Arrange — clsx skips falsy values, including 0

    // Act
    const result = cn("px-2", 0 as unknown as string);

    // Assert
    expect(result).toBe("px-2");
  });

  it("flattens an array of classes", () => {
    // Arrange
    const classes = ["px-2", "text-sm"];

    // Act
    const result = cn(classes);

    // Assert
    expect(result).toBe("px-2 text-sm");
  });

  it("flattens a nested array of classes", () => {
    // Arrange
    const classes = ["px-2", ["text-sm", ["font-bold"]]];

    // Act
    const result = cn(classes);

    // Assert
    expect(result).toBe("px-2 text-sm font-bold");
  });

  it("returns an empty string for an empty array", () => {
    // Arrange — nothing to merge

    // Act
    const result = cn([]);

    // Assert
    expect(result).toBe("");
  });

  it("includes object keys whose value is truthy", () => {
    // Arrange
    const conditions = { "px-2": true, "px-4": false };

    // Act
    const result = cn(conditions);

    // Assert
    expect(result).toBe("px-2");
  });

  it("returns an empty string for an object with all-falsy values", () => {
    // Arrange
    const conditions = { "px-2": false };

    // Act
    const result = cn(conditions);

    // Assert
    expect(result).toBe("");
  });

  it("returns an empty string for an empty object", () => {
    // Arrange — no keys to consider

    // Act
    const result = cn({});

    // Assert
    expect(result).toBe("");
  });

  it("collapses repeated whitespace between classes", () => {
    // Arrange — extra spaces inside a single string

    // Act
    const result = cn("px-2    text-sm");

    // Assert
    expect(result).toBe("px-2 text-sm");
  });

  it("normalizes tabs and newlines inside a class string", () => {
    // Arrange
    const messy = "px-2\n\ttext-sm";

    // Act
    const result = cn(messy);

    // Assert
    expect(result).toBe("px-2 text-sm");
  });

  it("returns an empty string for whitespace-only input", () => {
    // Arrange
    const whitespaceOnly = "   \t\n ";

    // Act
    const result = cn(whitespaceOnly);

    // Assert
    expect(result).toBe("");
  });

  it("passes through an arbitrary non-Tailwind class untouched", () => {
    // Arrange — project-specific classes must survive the merge

    // Act
    const result = cn("argos-panel", "px-2");

    // Assert
    expect(result).toBe("argos-panel px-2");
  });

  it("preserves an arbitrary-value Tailwind class", () => {
    // Arrange — bracket syntax must not be mangled

    // Act
    const result = cn("w-[calc(100%-2rem)]");

    // Assert
    expect(result).toBe("w-[calc(100%-2rem)]");
  });

  it("lets a later arbitrary-value class override an earlier one", () => {
    // Arrange — both target width

    // Act
    const result = cn("w-[10px]", "w-[20px]");

    // Assert
    expect(result).toBe("w-[20px]");
  });

  it("handles a very long class list without truncating", () => {
    // Arrange — distinct non-conflicting classes
    const many = Array.from(
      { length: LONG_CLASS_REPEAT },
      (_, index) => `argos-${index}`,
    );

    // Act
    const result = cn(many);

    // Assert
    expect(result.split(" ")).toHaveLength(LONG_CLASS_REPEAT);
  });

  it("keeps a class containing non-Latin characters", () => {
    // Arrange — unusual but valid as far as clsx is concerned

    // Act
    const result = cn("düğme-sınıfı");

    // Assert
    expect(result).toBe("düğme-sınıfı");
  });

  it("does not mutate an input array", () => {
    // Arrange
    const classes = ["px-2", "px-4"];
    const snapshot = [...classes];

    // Act
    cn(classes);

    // Assert
    expect(classes).toEqual(snapshot);
  });
});
