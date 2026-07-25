import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  installChromeMock,
  uninstallChromeMock,
  createPortMock,
  type ChromeMock,
  type PortMock,
} from "@/test/chrome-mock";
import { connectExecutionPort } from "./protocol";
import { EXECUTION_PORT_NAME } from "./types";
import type { BackgroundMessage, PanelMessage } from "./types";

const STEP_TIMEOUT = 5000;

let chromeMock: ChromeMock;
let port: PortMock;

const STEP_START_MESSAGE: BackgroundMessage = {
  type: "STEP_START",
  stepId: "step-1",
  stepIndex: 0,
};

const EXECUTE_STEPS_MESSAGE: PanelMessage = {
  type: "EXECUTE_STEPS",
  steps: [{ id: "step-1", command: "goto", params: { url: "https://a.test" } }],
  stepTimeout: STEP_TIMEOUT,
};

describe("connectExecutionPort", () => {
  beforeEach(() => {
    chromeMock = installChromeMock();
    port = createPortMock();
    chromeMock.runtime.connect.mockReturnValue(port);
  });

  afterEach(() => {
    uninstallChromeMock();
    vi.restoreAllMocks();
  });

  it("connects on the named execution port", () => {
    // Arrange
    const onMessage = vi.fn();

    // Act
    connectExecutionPort(onMessage);

    // Assert
    expect(chromeMock.runtime.connect).toHaveBeenCalledWith({
      name: EXECUTION_PORT_NAME,
    });
  });

  it("uses the port name the background listens for", () => {
    // Arrange — the literal must stay in sync with the background's guard

    // Act
    const name = EXECUTION_PORT_NAME;

    // Assert
    expect(name).toBe("argos-execution");
  });

  it("connects exactly once", () => {
    // Arrange
    const onMessage = vi.fn();

    // Act
    connectExecutionPort(onMessage);

    // Assert
    expect(chromeMock.runtime.connect).toHaveBeenCalledTimes(1);
  });

  it("registers the message listener on the port", () => {
    // Arrange
    const onMessage = vi.fn();

    // Act
    connectExecutionPort(onMessage);

    // Assert
    expect(port.onMessage.listenerCount).toBe(1);
  });

  it("forwards a background message to the callback", () => {
    // Arrange
    const onMessage = vi.fn();
    connectExecutionPort(onMessage);

    // Act
    port.onMessage.emit(STEP_START_MESSAGE);

    // Assert
    expect(onMessage).toHaveBeenCalledWith(STEP_START_MESSAGE);
  });

  it("forwards every message in order", () => {
    // Arrange
    const onMessage = vi.fn();
    connectExecutionPort(onMessage);

    // Act
    port.onMessage.emit(STEP_START_MESSAGE);
    port.onMessage.emit({
      type: "STEP_SUCCESS",
      stepId: "step-1",
      stepIndex: 0,
      duration: 12,
    });

    // Assert
    expect(onMessage.mock.calls.map((call) => (call[0] as { type: string }).type)).toEqual([
      "STEP_START",
      "STEP_SUCCESS",
    ]);
  });

  it("does not invoke the callback before a message arrives", () => {
    // Arrange
    const onMessage = vi.fn();

    // Act
    connectExecutionPort(onMessage);

    // Assert
    expect(onMessage).not.toHaveBeenCalled();
  });

  it("registers a disconnect listener when one is supplied", () => {
    // Arrange
    const onDisconnect = vi.fn();

    // Act
    connectExecutionPort(vi.fn(), onDisconnect);

    // Assert
    expect(port.onDisconnect.listenerCount).toBe(1);
  });

  it("invokes the disconnect callback when the port disconnects", () => {
    // Arrange
    const onDisconnect = vi.fn();
    connectExecutionPort(vi.fn(), onDisconnect);

    // Act
    port.onDisconnect.emit();

    // Assert
    expect(onDisconnect).toHaveBeenCalledTimes(1);
  });

  it("registers no disconnect listener when none is supplied", () => {
    // Arrange — the parameter is optional

    // Act
    connectExecutionPort(vi.fn());

    // Assert
    expect(port.onDisconnect.listenerCount).toBe(0);
  });

  it("posts a panel message through the port", () => {
    // Arrange
    const { send } = connectExecutionPort(vi.fn());

    // Act
    send(EXECUTE_STEPS_MESSAGE);

    // Assert
    expect(port.postMessage).toHaveBeenCalledWith(EXECUTE_STEPS_MESSAGE);
  });

  it("posts each message on its own call", () => {
    // Arrange
    const { send } = connectExecutionPort(vi.fn());

    // Act
    send(EXECUTE_STEPS_MESSAGE);
    send(EXECUTE_STEPS_MESSAGE);

    // Assert
    expect(port.postMessage).toHaveBeenCalledTimes(2);
  });

  it("posts nothing until send is called", () => {
    // Arrange — connecting must not emit anything on its own

    // Act
    connectExecutionPort(vi.fn());

    // Assert
    expect(port.postMessage).not.toHaveBeenCalled();
  });

  it("disconnects the underlying port", () => {
    // Arrange
    const { disconnect } = connectExecutionPort(vi.fn());

    // Act
    disconnect();

    // Assert
    expect(port.disconnect).toHaveBeenCalledTimes(1);
  });

  it("propagates a postMessage failure to the caller", () => {
    // Arrange — the panel is expected to handle a dead port itself
    port.postMessage.mockImplementation(() => {
      throw new Error("Attempting to use a disconnected port object");
    });
    const { send } = connectExecutionPort(vi.fn());

    // Act & Assert
    expect(() => send(EXECUTE_STEPS_MESSAGE)).toThrow(
      "Attempting to use a disconnected port object",
    );
  });

  it("gives each connection its own port", () => {
    // Arrange
    const secondPort = createPortMock();
    chromeMock.runtime.connect
      .mockReturnValueOnce(port)
      .mockReturnValueOnce(secondPort);

    // Act
    const first = connectExecutionPort(vi.fn());
    const second = connectExecutionPort(vi.fn());
    first.send(EXECUTE_STEPS_MESSAGE);
    second.send(EXECUTE_STEPS_MESSAGE);

    // Assert
    expect(secondPort.postMessage).toHaveBeenCalledTimes(1);
  });
});
