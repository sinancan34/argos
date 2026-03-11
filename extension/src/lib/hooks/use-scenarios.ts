import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getScenarios,
  getScenario,
  createScenario,
  updateScenario,
  deleteScenario,
} from "../api/scenarios";
import type {
  ScenarioCreate,
  ScenarioListParams,
  ScenarioUpdate,
} from "../schemas/scenario";

export function useScenarios(params: ScenarioListParams = {}) {
  return useQuery({
    queryKey: ["scenarios", params],
    queryFn: () => getScenarios(params),
  });
}

export function useScenario(id: string) {
  return useQuery({
    queryKey: ["scenarios", id],
    queryFn: () => getScenario(id),
    enabled: !!id,
  });
}

export function useCreateScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ScenarioCreate) => createScenario(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });
}

export function useUpdateScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ScenarioUpdate }) =>
      updateScenario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });
}

export function useDeleteScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteScenario(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });
}
