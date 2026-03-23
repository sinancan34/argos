import { executeSteps } from "./orchestrator";
import {
  EXECUTION_PORT_NAME,
  type SidePanelMessage,
} from "@/lib/messaging/types";

export default defineBackground(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === "PING") {
      sendResponse({ type: "PONG" });
    }
    return true;
  });

  chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== EXECUTION_PORT_NAME) return;

    let executing = false;

    port.onMessage.addListener((message: SidePanelMessage) => {
      if (executing) return;

      const mode =
        message.type === "EXECUTE_STEPS" ? "step-test" : "scenario-run";

      if (
        message.type === "EXECUTE_STEPS" ||
        message.type === "EXECUTE_SCENARIO"
      ) {
        executing = true;
        executeSteps(port, message.steps, message.stepTimeout, mode)
          .catch((err) => {
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
      }
    });
  });
});
