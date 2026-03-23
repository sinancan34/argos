// Command registry — data sourced from shared/commands.json (single source of truth).

import commandDefs from "../../../shared/commands.json";

export const selectorStrategies = commandDefs.selectorStrategies;

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

export const COMMANDS: CommandDef[] = commandDefs.commands as CommandDef[];

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
