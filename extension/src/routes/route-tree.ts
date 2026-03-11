import { rootRoute } from "./__root";
import { indexRoute } from "./index";
import { newScenarioRoute } from "./scenarios/new";
import { editScenarioRoute } from "./scenarios/$scenarioId/edit";

export const routeTree = rootRoute.addChildren([
  indexRoute,
  newScenarioRoute,
  editScenarioRoute,
]);
