import { describe, it, expect } from "vitest";
import { commandValues, COMMAND_MAP, COMMAND_CATEGORIES } from "./commands";

describe("command registry", () => {
  it("commandValues includes goto and click", () => {
    expect(commandValues).toContain("goto");
    expect(commandValues).toContain("click");
  });

  it("COMMAND_MAP has entries for all commands", () => {
    for (const cmd of commandValues) {
      expect(COMMAND_MAP.has(cmd)).toBe(true);
    }
  });

  it("COMMAND_MAP entries have params array", () => {
    const goto = COMMAND_MAP.get("goto");
    expect(goto).toBeDefined();
    expect(goto!.params.length).toBeGreaterThan(0);
    expect(goto!.params[0].name).toBe("url");
  });

  it("COMMAND_CATEGORIES groups by category", () => {
    expect(COMMAND_CATEGORIES.length).toBeGreaterThan(0);
    for (const cat of COMMAND_CATEGORIES) {
      expect(cat.category).toBeTruthy();
      expect(cat.commands.length).toBeGreaterThan(0);
    }
  });

  it("click command requires selector param", () => {
    const click = COMMAND_MAP.get("click");
    expect(click).toBeDefined();
    const selectorParam = click!.params.find((p) => p.name === "selector");
    expect(selectorParam).toBeDefined();
    expect(selectorParam!.required).toBe(true);
  });
});
