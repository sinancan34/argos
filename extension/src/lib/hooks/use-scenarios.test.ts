// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, cleanup, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import type { ScenarioCreate } from "../schemas/scenario";

const {
  getScenariosMock,
  getScenarioMock,
  createScenarioMock,
  updateScenarioMock,
  deleteScenarioMock,
} = vi.hoisted(() => ({
  getScenariosMock: vi.fn(),
  getScenarioMock: vi.fn(),
  createScenarioMock: vi.fn(),
  updateScenarioMock: vi.fn(),
  deleteScenarioMock: vi.fn(),
}));

vi.mock("../api/scenarios", () => ({
  getScenarios: (params: unknown) => getScenariosMock(params),
  getScenario: (id: string) => getScenarioMock(id),
  createScenario: (data: unknown) => createScenarioMock(data),
  updateScenario: (id: string, data: unknown) => updateScenarioMock(id, data),
  deleteScenario: (id: string) => deleteScenarioMock(id),
}));

import {
  useScenarios,
  useScenario,
  useCreateScenario,
  useUpdateScenario,
  useDeleteScenario,
} from "./use-scenarios";

const SCENARIO_ID = "scenario-1";
const LIST_ENVELOPE = { data: [], meta: {}, links: {} };
const SINGLE_ENVELOPE = { data: { id: SCENARIO_ID, name: "Checkout flow" } };

const CREATE_PAYLOAD = {
  name: "Checkout flow",
  device_id: "device-1",
  status: true,
  step_timeout: 5000,
  validation_timeout: 10000,
  steps: [],
  validations: [],
} as unknown as ScenarioCreate;

let queryClient: QueryClient;

function wrapper({ children }: { children: ReactNode }) {
  return createElement(QueryClientProvider, { client: queryClient }, children);
}

function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
}

describe("useScenarios", () => {
  beforeEach(() => {
    queryClient = makeQueryClient();
    getScenariosMock.mockReset();
    getScenariosMock.mockResolvedValue(LIST_ENVELOPE);
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("fetches the scenario list", async () => {
    // Arrange & Act
    const { result } = renderHook(() => useScenarios(), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.data).toEqual(LIST_ENVELOPE));
  });

  it("calls the API with no params by default", async () => {
    // Arrange & Act
    renderHook(() => useScenarios(), { wrapper });

    // Assert
    await waitFor(() => expect(getScenariosMock).toHaveBeenCalledWith({}));
  });

  it("forwards list params to the API", async () => {
    // Arrange
    const params = { name: "checkout", status: true, page: 2 };

    // Act
    renderHook(() => useScenarios(params), { wrapper });

    // Assert
    await waitFor(() => expect(getScenariosMock).toHaveBeenCalledWith(params));
  });

  it("refetches when the params change", async () => {
    // Arrange
    const { rerender } = renderHook(({ page }) => useScenarios({ page }), {
      wrapper,
      initialProps: { page: 1 },
    });
    await waitFor(() => expect(getScenariosMock).toHaveBeenCalledTimes(1));

    // Act
    rerender({ page: 2 });

    // Assert
    await waitFor(() => expect(getScenariosMock).toHaveBeenCalledTimes(2));
  });

  it("surfaces a request failure", async () => {
    // Arrange
    getScenariosMock.mockRejectedValue(new Error("Network error"));

    // Act
    const { result } = renderHook(() => useScenarios(), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe("useScenario", () => {
  beforeEach(() => {
    queryClient = makeQueryClient();
    getScenarioMock.mockReset();
    getScenarioMock.mockResolvedValue(SINGLE_ENVELOPE);
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("fetches the scenario by id", async () => {
    // Arrange & Act
    const { result } = renderHook(() => useScenario(SCENARIO_ID), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.data).toEqual(SINGLE_ENVELOPE));
  });

  it("does not fetch for an empty id", () => {
    // Arrange & Act
    renderHook(() => useScenario(""), { wrapper });

    // Assert
    expect(getScenarioMock).not.toHaveBeenCalled();
  });

  it("fetches once the id becomes available", async () => {
    // Arrange
    const { rerender } = renderHook(({ id }) => useScenario(id), {
      wrapper,
      initialProps: { id: "" },
    });

    // Act
    rerender({ id: SCENARIO_ID });

    // Assert
    await waitFor(() =>
      expect(getScenarioMock).toHaveBeenCalledWith(SCENARIO_ID),
    );
  });
});

describe("useCreateScenario", () => {
  beforeEach(() => {
    queryClient = makeQueryClient();
    createScenarioMock.mockReset();
    createScenarioMock.mockResolvedValue(SINGLE_ENVELOPE);
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("posts the payload to the API", async () => {
    // Arrange
    const { result } = renderHook(() => useCreateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(CREATE_PAYLOAD));

    // Assert
    await waitFor(() =>
      expect(createScenarioMock).toHaveBeenCalledWith(CREATE_PAYLOAD),
    );
  });

  it("reports success", async () => {
    // Arrange
    const { result } = renderHook(() => useCreateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(CREATE_PAYLOAD));

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it("invalidates the scenario list on success", async () => {
    // Arrange
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    const { result } = renderHook(() => useCreateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(CREATE_PAYLOAD));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Assert
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["scenarios"] });
  });

  it("does not invalidate on failure", async () => {
    // Arrange
    createScenarioMock.mockRejectedValue(new Error("Validation failed"));
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    const { result } = renderHook(() => useCreateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(CREATE_PAYLOAD));
    await waitFor(() => expect(result.current.isError).toBe(true));

    // Assert
    expect(invalidateSpy).not.toHaveBeenCalled();
  });

  it("surfaces the failure to the caller", async () => {
    // Arrange
    createScenarioMock.mockRejectedValue(new Error("Validation failed"));
    const { result } = renderHook(() => useCreateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(CREATE_PAYLOAD));

    // Assert
    await waitFor(() =>
      expect(result.current.error?.message).toBe("Validation failed"),
    );
  });
});

describe("useUpdateScenario", () => {
  beforeEach(() => {
    queryClient = makeQueryClient();
    updateScenarioMock.mockReset();
    updateScenarioMock.mockResolvedValue(SINGLE_ENVELOPE);
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("splits the id and body for the API call", async () => {
    // Arrange
    const { result } = renderHook(() => useUpdateScenario(), { wrapper });

    // Act
    act(() =>
      result.current.mutate({ id: SCENARIO_ID, data: { status: false } }),
    );

    // Assert
    await waitFor(() =>
      expect(updateScenarioMock).toHaveBeenCalledWith(SCENARIO_ID, {
        status: false,
      }),
    );
  });

  it("invalidates the scenario list on success", async () => {
    // Arrange
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    const { result } = renderHook(() => useUpdateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate({ id: SCENARIO_ID, data: {} }));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Assert
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["scenarios"] });
  });

  it("surfaces a failure", async () => {
    // Arrange
    updateScenarioMock.mockRejectedValue(new Error("Conflict"));
    const { result } = renderHook(() => useUpdateScenario(), { wrapper });

    // Act
    act(() => result.current.mutate({ id: SCENARIO_ID, data: {} }));

    // Assert
    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe("useDeleteScenario", () => {
  beforeEach(() => {
    queryClient = makeQueryClient();
    deleteScenarioMock.mockReset();
    deleteScenarioMock.mockResolvedValue({ data: { id: SCENARIO_ID } });
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("passes the id to the API", async () => {
    // Arrange
    const { result } = renderHook(() => useDeleteScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(SCENARIO_ID));

    // Assert
    await waitFor(() =>
      expect(deleteScenarioMock).toHaveBeenCalledWith(SCENARIO_ID),
    );
  });

  it("invalidates the scenario list on success", async () => {
    // Arrange
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    const { result } = renderHook(() => useDeleteScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(SCENARIO_ID));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Assert
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["scenarios"] });
  });

  it("reports the pending state while in flight", async () => {
    // Arrange
    deleteScenarioMock.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useDeleteScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(SCENARIO_ID));

    // Assert
    await waitFor(() => expect(result.current.isPending).toBe(true));
  });

  it("surfaces a failure", async () => {
    // Arrange
    deleteScenarioMock.mockRejectedValue(new Error("Forbidden"));
    const { result } = renderHook(() => useDeleteScenario(), { wrapper });

    // Act
    act(() => result.current.mutate(SCENARIO_ID));

    // Assert
    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
