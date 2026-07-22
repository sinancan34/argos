import {
  EXECUTION_PORT_NAME,
  type PanelMessage,
  type BackgroundMessage,
} from "./types";

export function connectExecutionPort(
  onMessage: (message: BackgroundMessage) => void,
  onDisconnect?: () => void,
): {
  send: (message: PanelMessage) => void;
  disconnect: () => void;
} {
  const port = chrome.runtime.connect({ name: EXECUTION_PORT_NAME });

  port.onMessage.addListener(onMessage);

  if (onDisconnect) {
    port.onDisconnect.addListener(onDisconnect);
  }

  return {
    send: (message: PanelMessage) => port.postMessage(message),
    disconnect: () => port.disconnect(),
  };
}
