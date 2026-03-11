// Command registry — single source of truth for step commands and their parameters.

export const selectorStrategies = [
  "css",
  "xpath",
  "linkText",
] as const;

export type SelectorStrategy = (typeof selectorStrategies)[number];

export interface SelectorEntry {
  strategy: SelectorStrategy;
  value: string;
}

export interface CommandParamDef {
  name: string;
  type: "string" | "int" | "selector";
  required: boolean;
  placeholder?: string;
}

export interface CommandDef {
  command: string;
  category: string;
  params: CommandParamDef[];
}

export const COMMANDS: CommandDef[] = [
  // Navigation
  {
    command: "goto",
    category: "Navigation",
    params: [
      { name: "url", type: "string", required: true, placeholder: "https://example.com" },
    ],
  },
  // Element Interaction
  {
    command: "click",
    category: "Element Interaction",
    params: [
      { name: "selector", type: "selector", required: true },
    ],
  },
];

export const commandValues = COMMANDS.map((c) => c.command) as [string, ...string[]];

export const COMMAND_MAP = new Map<string, CommandDef>(
  COMMANDS.map((c) => [c.command, c]),
);

export const COMMAND_CATEGORIES = Object.entries(
  COMMANDS.reduce<Record<string, CommandDef[]>>((acc, cmd) => {
    (acc[cmd.category] ??= []).push(cmd);
    return acc;
  }, {}),
).map(([category, commands]) => ({ category, commands }));
