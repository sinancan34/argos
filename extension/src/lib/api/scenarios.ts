import { api } from "./client";
import type {
  ScenarioCreate,
  ScenarioListEnvelope,
  ScenarioListParams,
  ScenarioUpdate,
  SingleScenarioEnvelope,
} from "../schemas/scenario";

export async function getScenarios(
  params: ScenarioListParams = {},
): Promise<ScenarioListEnvelope> {
  const searchParams = new URLSearchParams();

  if (params.name) searchParams.set("name", params.name);
  if (params.status !== undefined) searchParams.set("status", String(params.status));
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.sort_order) searchParams.set("sort_order", params.sort_order);
  if (params.page) searchParams.set("page", String(params.page));
  if (params.size) searchParams.set("size", String(params.size));

  return api.get("scenarios", { searchParams }).json<ScenarioListEnvelope>();
}

export async function getScenario(id: string): Promise<SingleScenarioEnvelope> {
  return api.get(`scenarios/${id}`).json<SingleScenarioEnvelope>();
}

export async function createScenario(
  data: ScenarioCreate,
): Promise<SingleScenarioEnvelope> {
  return api.post("scenarios", { json: data }).json<SingleScenarioEnvelope>();
}

export async function updateScenario(
  id: string,
  data: ScenarioUpdate,
): Promise<SingleScenarioEnvelope> {
  return api.patch(`scenarios/${id}`, { json: data }).json<SingleScenarioEnvelope>();
}

export async function deleteScenario(id: string): Promise<void> {
  await api.delete(`scenarios/${id}`);
}
