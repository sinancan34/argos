import { executeSteps } from "./orchestrator";
import {
  EXECUTION_PORT_NAME,
  type PanelMessage,
} from "@/lib/messaging/types";

export default defineBackground(() => {
  let executing = false;
  let pickerActive = false;
  let pickerTabId: number | null = null;

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === "PING") {
      sendResponse({ type: "PONG" });
      return true;
    }

    if (message.type === "PICKER_START") {
      if (pickerActive || executing) {
        sendResponse({ success: false, error: "Another operation is in progress" });
        return true;
      }

      // The panel supplies the inspected tab explicitly. Guessing it here (e.g.
      // via tabs.query) would target the wrong window whenever DevTools is
      // undocked, so an absent tabId is an error rather than a fallback.
      const targetTabId: unknown = message.tabId;

      if (typeof targetTabId !== "number") {
        sendResponse({ success: false, error: "No target tab supplied" });
        return true;
      }

      pickerActive = true;
      pickerTabId = targetTabId;
      chrome.scripting
        .executeScript({
          target: { tabId: targetTabId },
          files: ["/content-scripts/picker.js"],
        })
        .then(() => {
          sendResponse({ success: true, tabId: targetTabId });
        })
        .catch((err: unknown) => {
          pickerActive = false;
          pickerTabId = null;
          const error = err instanceof Error ? err.message : String(err);
          sendResponse({ success: false, error });
        });
      return true;
    }

    if (message.type === "PICKER_CANCEL") {
      if (pickerTabId !== null) {
        chrome.tabs.sendMessage(pickerTabId, { type: "PICKER_CANCEL" }).catch(() => {});
      }
      pickerActive = false;
      pickerTabId = null;
      sendResponse({ success: true });
      return true;
    }

    // Relay picker result/error from content script to the DevTools panel
    if (message.type === "PICKER_RESULT" || message.type === "PICKER_ERROR") {
      pickerActive = false;
      pickerTabId = null;
      // Don't sendResponse — let the message propagate to other listeners (panel)
      return false;
    }

    return true;
  });

  chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== EXECUTION_PORT_NAME) return;

    port.onMessage.addListener((message: PanelMessage) => {
      if (executing || pickerActive) return;

      const mode =
        message.type === "EXECUTE_STEPS" ? "step-test" : "scenario-run";

      if (message.type === "EXECUTE_STEPS") {
        executing = true;
        executeSteps(port, message.steps, message.stepTimeout, mode)
          .catch(() => {
            try {
              port.postMessage({
                type: "EXECUTION_COMPLETE",
                mode,
                success: false,
                stepResults: [],
              });
            } catch {
              // Port already disconnected
            }
          })
          .finally(() => {
            executing = false;
          });
      } else if (message.type === "EXECUTE_SCENARIO") {
        executing = true;
        executeSteps(
          port,
          message.steps,
          message.stepTimeout,
          mode,
          message.validations,
          message.validationTimeout,
        )
          .catch(() => {
            try {
              port.postMessage({
                type: "EXECUTION_COMPLETE",
                mode,
                success: false,
                stepResults: [],
                validationResults: [],
              });
            } catch {
              // Port already disconnected
            }
          })
          .finally(() => {
            executing = false;
          });
      }
    });
  });
});
