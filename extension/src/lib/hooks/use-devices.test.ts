// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

const { getDevicesMock, getDeviceMock } = vi.hoisted(() => ({
  getDevicesMock: vi.fn(),
  getDeviceMock: vi.fn(),
}));

vi.mock("../api/devices", () => ({
  getDevices: (params: unknown) => getDevicesMock(params),
  getDevice: (id: string) => getDeviceMock(id),
}));

import { useDevices, useDevice } from "./use-devices";

const DEVICE_ID = "device-1";
const LIST_ENVELOPE = { data: [], meta: {}, links: {} };
const SINGLE_ENVELOPE = { data: { id: DEVICE_ID, name: "iPhone SE" } };

let queryClient: QueryClient;

function wrapper({ children }: { children: ReactNode }) {
  return createElement(QueryClientProvider, { client: queryClient }, children);
}

describe("useDevices", () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    getDevicesMock.mockReset();
    getDevicesMock.mockResolvedValue(LIST_ENVELOPE);
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("fetches the device list", async () => {
    // Arrange & Act
    const { result } = renderHook(() => useDevices(), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.data).toEqual(LIST_ENVELOPE));
  });

  it("calls the API with no params by default", async () => {
    // Arrange & Act
    renderHook(() => useDevices(), { wrapper });

    // Assert
    await waitFor(() => expect(getDevicesMock).toHaveBeenCalledWith({}));
  });

  it("forwards the given params to the API", async () => {
    // Arrange
    const params = { status: true, name: "pixel", size: 100 };

    // Act
    renderHook(() => useDevices(params), { wrapper });

    // Assert
    await waitFor(() => expect(getDevicesMock).toHaveBeenCalledWith(params));
  });

  it("caches by params, so identical params fetch once", async () => {
    // Arrange
    const params = { status: true };

    // Act
    renderHook(() => useDevices(params), { wrapper });
    renderHook(() => useDevices({ status: true }), { wrapper });

    // Assert
    await waitFor(() => expect(getDevicesMock).toHaveBeenCalledTimes(1));
  });

  it("refetches when the params change", async () => {
    // Arrange
    const { rerender } = renderHook(({ name }) => useDevices({ name }), {
      wrapper,
      initialProps: { name: "pixel" },
    });
    await waitFor(() => expect(getDevicesMock).toHaveBeenCalledTimes(1));

    // Act
    rerender({ name: "iphone" });

    // Assert
    await waitFor(() => expect(getDevicesMock).toHaveBeenCalledTimes(2));
  });

  it("keeps the previous list visible while a new search is in flight", async () => {
    // Arrange — placeholderData: keepPreviousData avoids a flash of empty
    const firstEnvelope = { data: [{ id: "a" }], meta: {}, links: {} };
    getDevicesMock.mockResolvedValueOnce(firstEnvelope);
    const { result, rerender } = renderHook(
      ({ name }) => useDevices({ name }),
      { wrapper, initialProps: { name: "pixel" } },
    );
    await waitFor(() => expect(result.current.data).toEqual(firstEnvelope));

    // Act
    getDevicesMock.mockReturnValue(new Promise(() => {}));
    rerender({ name: "iphone" });

    // Assert
    expect(result.current.data).toEqual(firstEnvelope);
  });

  it("surfaces a request failure", async () => {
    // Arrange
    getDevicesMock.mockRejectedValue(new Error("Network error"));

    // Act
    const { result } = renderHook(() => useDevices(), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.isError).toBe(true));
  });

  it("starts in the loading state", () => {
    // Arrange & Act
    const { result } = renderHook(() => useDevices(), { wrapper });

    // Assert
    expect(result.current.isLoading).toBe(true);
  });
});

describe("useDevice", () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    getDeviceMock.mockReset();
    getDeviceMock.mockResolvedValue(SINGLE_ENVELOPE);
  });

  afterEach(() => {
    cleanup();
    queryClient.clear();
    vi.restoreAllMocks();
  });

  it("fetches the device by id", async () => {
    // Arrange & Act
    const { result } = renderHook(() => useDevice(DEVICE_ID), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.data).toEqual(SINGLE_ENVELOPE));
  });

  it("passes the id to the API", async () => {
    // Arrange & Act
    renderHook(() => useDevice(DEVICE_ID), { wrapper });

    // Assert
    await waitFor(() => expect(getDeviceMock).toHaveBeenCalledWith(DEVICE_ID));
  });

  it("does not fetch for an empty id", () => {
    // Arrange & Act
    renderHook(() => useDevice(""), { wrapper });

    // Assert
    expect(getDeviceMock).not.toHaveBeenCalled();
  });

  it("stays disabled for an empty id", () => {
    // Arrange & Act
    const { result } = renderHook(() => useDevice(""), { wrapper });

    // Assert
    expect(result.current.fetchStatus).toBe("idle");
  });

  it("fetches once the id becomes available", async () => {
    // Arrange
    const { rerender } = renderHook(({ id }) => useDevice(id), {
      wrapper,
      initialProps: { id: "" },
    });

    // Act
    rerender({ id: DEVICE_ID });

    // Assert
    await waitFor(() => expect(getDeviceMock).toHaveBeenCalledWith(DEVICE_ID));
  });

  it("caches separate ids independently", async () => {
    // Arrange & Act
    renderHook(() => useDevice(DEVICE_ID), { wrapper });
    renderHook(() => useDevice("device-2"), { wrapper });

    // Assert
    await waitFor(() => expect(getDeviceMock).toHaveBeenCalledTimes(2));
  });

  it("surfaces a request failure", async () => {
    // Arrange
    getDeviceMock.mockRejectedValue(new Error("Not found"));

    // Act
    const { result } = renderHook(() => useDevice(DEVICE_ID), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
