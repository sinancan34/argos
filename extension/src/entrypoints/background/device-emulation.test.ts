import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  installChromeMock,
  uninstallChromeMock,
  type ChromeMock,
} from "@/test/chrome-mock";
import { applyDeviceEmulation, detachDeviceEmulation } from "./device-emulation";
import type { EmulationParams } from "@/lib/devices/emulation-params";

const TAB_ID = 42;
const PROTOCOL_VERSION = "1.3";

const SET_DEVICE_METRICS = "Emulation.setDeviceMetricsOverride";
const SET_USER_AGENT = "Emulation.setUserAgentOverride";
const SET_TOUCH = "Emulation.setTouchEmulationEnabled";

let chromeMock: ChromeMock;

function makeParams(overrides: Partial<EmulationParams> = {}): EmulationParams {
  return {
    deviceMetrics: {
      width: 375,
      height: 667,
      deviceScaleFactor: 2,
      mobile: true,
    },
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5) Safari/604.1",
    touch: { enabled: true, maxTouchPoints: 1 },
    ...overrides,
  };
}

/** CDP command names sent, in order. */
function sentCommands(): string[] {
  return chromeMock.debugger.sendCommand.mock.calls.map(
    (call) => call[1] as string,
  );
}

/** Payload of the first sendCommand call for the given CDP method. */
function payloadFor(method: string): Record<string, unknown> | undefined {
  const call = chromeMock.debugger.sendCommand.mock.calls.find(
    (c) => c[1] === method,
  );
  return call?.[2] as Record<string, unknown> | undefined;
}

describe("applyDeviceEmulation", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    chromeMock.debugger.attach.mockResolvedValue(undefined);
    chromeMock.debugger.sendCommand.mockResolvedValue(undefined);
    chromeMock.debugger.detach.mockResolvedValue(undefined);
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.restoreAllMocks();
  });

  it("returns true when attach and every command succeed", async () => {
    // Arrange
    const params = makeParams();

    // Act
    const result = await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(result).toBe(true);
  });

  it("attaches the debugger to the given tab", async () => {
    // Arrange
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(chromeMock.debugger.attach).toHaveBeenCalledWith(
      { tabId: TAB_ID },
      PROTOCOL_VERSION,
    );
  });

  it("attaches exactly once", async () => {
    // Arrange
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(chromeMock.debugger.attach).toHaveBeenCalledTimes(1);
  });

  it("sends the device metrics override with the params it was given", async () => {
    // Arrange
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(payloadFor(SET_DEVICE_METRICS)).toEqual({
      width: 375,
      height: 667,
      deviceScaleFactor: 2,
      mobile: true,
    });
  });

  it("targets the debuggee tab on every command", async () => {
    // Arrange
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    const targets = chromeMock.debugger.sendCommand.mock.calls.map((c) => c[0]);
    expect(targets.every((t) => (t as { tabId: number }).tabId === TAB_ID)).toBe(
      true,
    );
  });

  it("sends the user agent override when a user agent is present", async () => {
    // Arrange
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(payloadFor(SET_USER_AGENT)).toEqual({
      userAgent: params.userAgent,
    });
  });

  it("omits the user agent override when the user agent is undefined", async () => {
    // Arrange
    const params = makeParams({ userAgent: undefined });

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(sentCommands()).not.toContain(SET_USER_AGENT);
  });

  it("omits the user agent override for an empty user agent string", async () => {
    // Arrange — an empty string is falsy, so the override is skipped
    const params = makeParams({ userAgent: "" });

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(sentCommands()).not.toContain(SET_USER_AGENT);
  });

  it("sends the touch override with enabled state and max touch points", async () => {
    // Arrange
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(payloadFor(SET_TOUCH)).toEqual({
      enabled: true,
      maxTouchPoints: 1,
    });
  });

  it("sends a disabled touch override for a non-touch device", async () => {
    // Arrange
    const params = makeParams({ touch: { enabled: false, maxTouchPoints: 0 } });

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(payloadFor(SET_TOUCH)).toEqual({
      enabled: false,
      maxTouchPoints: 0,
    });
  });

  it("sends metrics before user agent before touch", async () => {
    // Arrange — the viewport must be set before the page reads it
    const params = makeParams();

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(sentCommands()).toEqual([
      SET_DEVICE_METRICS,
      SET_USER_AGENT,
      SET_TOUCH,
    ]);
  });

  it("sends two commands when the user agent is absent", async () => {
    // Arrange
    const params = makeParams({ userAgent: undefined });

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(sentCommands()).toEqual([SET_DEVICE_METRICS, SET_TOUCH]);
  });

  it("passes a desktop viewport through unchanged", async () => {
    // Arrange
    const params = makeParams({
      deviceMetrics: {
        width: 1920,
        height: 1080,
        deviceScaleFactor: 1,
        mobile: false,
      },
      touch: { enabled: false, maxTouchPoints: 0 },
    });

    // Act
    await applyDeviceEmulation(TAB_ID, params);

    // Assert
    expect(payloadFor(SET_DEVICE_METRICS)).toEqual({
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1,
      mobile: false,
    });
  });

  it("returns false when attach fails", async () => {
    // Arrange — e.g. another debugger already owns the tab
    chromeMock.debugger.attach.mockRejectedValue(new Error("already attached"));

    // Act
    const result = await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(result).toBe(false);
  });

  it("sends no CDP commands when attach fails", async () => {
    // Arrange
    chromeMock.debugger.attach.mockRejectedValue(new Error("already attached"));

    // Act
    await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(chromeMock.debugger.sendCommand).not.toHaveBeenCalled();
  });

  it("does not detach when attach fails", async () => {
    // Arrange — nothing was attached, so there is nothing to clean up
    chromeMock.debugger.attach.mockRejectedValue(new Error("already attached"));

    // Act
    await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(chromeMock.debugger.detach).not.toHaveBeenCalled();
  });

  it("returns false when the metrics command fails", async () => {
    // Arrange
    chromeMock.debugger.sendCommand.mockRejectedValue(new Error("CDP error"));

    // Act
    const result = await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(result).toBe(false);
  });

  it("detaches when a command fails after a successful attach", async () => {
    // Arrange — otherwise the debugger banner would stay up
    chromeMock.debugger.sendCommand.mockRejectedValue(new Error("CDP error"));

    // Act
    await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(chromeMock.debugger.detach).toHaveBeenCalledWith({ tabId: TAB_ID });
  });

  it("returns false when only the user agent command fails", async () => {
    // Arrange
    chromeMock.debugger.sendCommand.mockImplementation(
      (_target: unknown, method: string) =>
        method === SET_USER_AGENT
          ? Promise.reject(new Error("UA rejected"))
          : Promise.resolve(undefined),
    );

    // Act
    const result = await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(result).toBe(false);
  });

  it("returns false when only the touch command fails", async () => {
    // Arrange
    chromeMock.debugger.sendCommand.mockImplementation(
      (_target: unknown, method: string) =>
        method === SET_TOUCH
          ? Promise.reject(new Error("touch rejected"))
          : Promise.resolve(undefined),
    );

    // Act
    const result = await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(result).toBe(false);
  });

  it("stops sending commands after the first failure", async () => {
    // Arrange
    chromeMock.debugger.sendCommand.mockImplementation(
      (_target: unknown, method: string) =>
        method === SET_DEVICE_METRICS
          ? Promise.reject(new Error("CDP error"))
          : Promise.resolve(undefined),
    );

    // Act
    await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(sentCommands()).toEqual([SET_DEVICE_METRICS]);
  });

  it("returns false rather than throwing when the detach during cleanup also fails", async () => {
    // Arrange — both the command and the cleanup detach reject
    chromeMock.debugger.sendCommand.mockRejectedValue(new Error("CDP error"));
    chromeMock.debugger.detach.mockRejectedValue(new Error("no target"));

    // Act
    const result = await applyDeviceEmulation(TAB_ID, makeParams());

    // Assert
    expect(result).toBe(false);
  });

  it("attaches to tab id 0 rather than treating it as absent", async () => {
    // Arrange — 0 is a valid tab id and must not be dropped by a truthiness check
    const zeroTabId = 0;

    // Act
    await applyDeviceEmulation(zeroTabId, makeParams());

    // Assert
    expect(chromeMock.debugger.attach).toHaveBeenCalledWith(
      { tabId: zeroTabId },
      PROTOCOL_VERSION,
    );
  });
});

describe("detachDeviceEmulation", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    chromeMock.debugger.detach.mockResolvedValue(undefined);
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.restoreAllMocks();
  });

  it("detaches the debugger from the given tab", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await detachDeviceEmulation(TAB_ID);

    // Assert
    expect(chromeMock.debugger.detach).toHaveBeenCalledWith({ tabId: TAB_ID });
  });

  it("detaches exactly once", async () => {
    // Arrange — mock configured in beforeEach

    // Act
    await detachDeviceEmulation(TAB_ID);

    // Assert
    expect(chromeMock.debugger.detach).toHaveBeenCalledTimes(1);
  });

  it("resolves when the tab is already gone", async () => {
    // Arrange — detaching from a removed target rejects, which must be swallowed
    chromeMock.debugger.detach.mockRejectedValue(new Error("No target"));

    // Act & Assert
    await expect(detachDeviceEmulation(TAB_ID)).resolves.toBeUndefined();
  });

  it("resolves when the debugger was never attached", async () => {
    // Arrange
    chromeMock.debugger.detach.mockRejectedValue(
      new Error("Debugger is not attached"),
    );

    // Act & Assert
    await expect(detachDeviceEmulation(TAB_ID)).resolves.toBeUndefined();
  });

  it("swallows a non-Error rejection value", async () => {
    // Arrange — chrome can reject with a plain string
    chromeMock.debugger.detach.mockRejectedValue("no target");

    // Act & Assert
    await expect(detachDeviceEmulation(TAB_ID)).resolves.toBeUndefined();
  });

  it("detaches from tab id 0", async () => {
    // Arrange
    const zeroTabId = 0;

    // Act
    await detachDeviceEmulation(zeroTabId);

    // Assert
    expect(chromeMock.debugger.detach).toHaveBeenCalledWith({ tabId: 0 });
  });
});
