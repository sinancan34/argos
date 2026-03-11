import type { Message } from "./types";

export function sendMessage(message: Message): Promise<Message> {
  return chrome.runtime.sendMessage(message);
}

export function onMessage(handler: (message: Message) => void): void {
  chrome.runtime.onMessage.addListener((message: Message) => {
    handler(message);
  });
}
