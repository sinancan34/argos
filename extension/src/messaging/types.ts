export type Message =
  | { type: "PING" }
  | { type: "PONG" }
  | { type: "RUN_SCENARIO"; payload: { scenarioId: string } };
