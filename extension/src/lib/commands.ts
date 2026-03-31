// Command registry — data sourced from shared/commands.json (single source of truth).

import commandDefs from "../../../shared/commands.json";

interface CommandParamDef {
  name: string;
  type: "string" | "int";
  required: boolean;
  placeholder?: string;
}

interface CommandDef {
  command: string;
  category: string;
  params: CommandParamDef[];
}

const COMMANDS: CommandDef[] = commandDefs.commands as CommandDef[];

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
