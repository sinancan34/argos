import type { Step } from "@/lib/schemas/scenario";
import type { SelectorEntry } from "@/lib/commands";
import type { StepResult } from "@/lib/executor/types";
import type { BackgroundMessage } from "@/lib/messaging/types";

function postMessage(port: chrome.runtime.Port, message: BackgroundMessage) {
  try {
    port.postMessage(message);
  } catch {
    // Port disconnected — ignore silently
  }
}

interface CancellablePromise<T> {
  promise: Promise<T>;
  cleanup: () => void;
}

function waitForNavigation(tabId: number): CancellablePromise<void> {
  let listener: (
    details: chrome.webNavigation.WebNavigationFramedCallbackDetails,
  ) => void;
  let errorListener: (
    details: chrome.webNavigation.WebNavigationFramedErrorCallbackDetails,
  ) => void;

  const cleanup = () => {
    chrome.webNavigation.onCompleted.removeListener(listener);
    chrome.webNavigation.onErrorOccurred.removeListener(errorListener);
  };

  const promise = new Promise<void>((resolve, reject) => {
    listener = (details) => {
      if (details.tabId === tabId && details.frameId === 0) {
        cleanup();
        resolve();
      }
    };

    errorListener = (details) => {
      if (details.tabId === tabId && details.frameId === 0) {
        cleanup();
        reject(new Error(`Navigation failed: ${details.error}`));
      }
    };

    chrome.webNavigation.onCompleted.addListener(listener);
    chrome.webNavigation.onErrorOccurred.addListener(errorListener);
  });

  return { promise, cleanup };
}

function waitForContentReady(tabId: number): CancellablePromise<void> {
  let listener: (
    message: { type: string },
    sender: chrome.runtime.MessageSender,
  ) => void;

  const cleanup = () => {
    chrome.runtime.onMessage.removeListener(listener);
  };

  const promise = new Promise<void>((resolve) => {
    listener = (message, sender) => {
      if (message.type === "CONTENT_READY" && sender.tab?.id === tabId) {
        cleanup();
        resolve();
      }
    };

    chrome.runtime.onMessage.addListener(listener);
  });

  return { promise, cleanup };
}

function cancellableTimeout(
  ms: number,
  label: string,
): CancellablePromise<never> {
  let timerId: ReturnType<typeof setTimeout>;

  const cleanup = () => clearTimeout(timerId);

  const promise = new Promise<never>((_, reject) => {
    timerId = setTimeout(
      () => reject(new Error(`Timeout after ${ms}ms: ${label}`)),
      ms,
    );
  });

  return { promise, cleanup };
}

async function executeGoto(tabId: number, url: string): Promise<void> {
  const nav = waitForNavigation(tabId);
  try {
    await chrome.tabs.update(tabId, { url });
    await nav.promise;
  } finally {
    nav.cleanup();
  }

  const ready = waitForContentReady(tabId);
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ["content-scripts/content.js"],
    });
    await ready.promise;
  } finally {
    ready.cleanup();
  }
}

async function executeClick(
  tabId: number,
  selectors: SelectorEntry[],
): Promise<void> {
  const response = await chrome.tabs.sendMessage(tabId, {
    type: "EXEC_CLICK",
    selectors,
  });

  if (!response?.success) {
    throw new Error(response?.error ?? "Click failed");
  }
}

async function executeCommand(tabId: number, step: Step): Promise<void> {
  switch (step.command) {
    case "goto": {
      const url = step.params.url as string;
      if (!url) throw new Error("goto step missing 'url' param");
      await executeGoto(tabId, url);
      break;
    }
    case "click": {
      const selectors = step.params.selector as SelectorEntry[];
      if (!selectors?.length)
        throw new Error("click step missing 'selector' param");
      await executeClick(tabId, selectors);
      break;
    }
    default:
      throw new Error(`Unknown command: ${step.command}`);
  }
}

export async function executeSteps(
  port: chrome.runtime.Port,
  steps: Step[],
  defaultTimeout: number,
  mode: "step-test" | "scenario-run",
): Promise<void> {
  const stepResults: StepResult[] = [];
  let aborted = false;
  let tabClosed = false;
  let tabClosedReject: ((error: Error) => void) | null = null;

  const tab = await chrome.tabs.create({ url: "about:blank", active: true });
  if (!tab.id) throw new Error("Failed to create execution tab");
  const tabId = tab.id;

  const onTabRemoved = (removedTabId: number) => {
    if (removedTabId === tabId) {
      tabClosed = true;
      tabClosedReject?.(new Error("Execution tab was closed"));
    }
  };

  const onDisconnect = () => {
    aborted = true;
  };

  chrome.tabs.onRemoved.addListener(onTabRemoved);
  port.onDisconnect.addListener(onDisconnect);

  try {
    for (let i = 0; i < steps.length; i++) {
      if (aborted || tabClosed) break;

      const step = steps[i];
      const effectiveTimeout = defaultTimeout;
      const startTime = Date.now();

      postMessage(port, {
        type: "STEP_START",
        stepId: step.id,
        stepIndex: i,
      });

      const timeout = cancellableTimeout(effectiveTimeout, step.command);

      try {
        const tabClosedPromise = new Promise<never>((_, reject) => {
          if (tabClosed) {
            reject(new Error("Execution tab was closed"));
            return;
          }
          tabClosedReject = reject;
        });

        await Promise.race([
          executeCommand(tabId, step),
          timeout.promise,
          tabClosedPromise,
        ]);

        const duration = Date.now() - startTime;
        stepResults.push({
          stepId: step.id,
          command: step.command,
          status: "success",
          duration,
        });

        postMessage(port, {
          type: "STEP_SUCCESS",
          stepId: step.id,
          stepIndex: i,
          duration,
        });
      } catch (error) {
        const duration = Date.now() - startTime;
        const errorMessage =
          error instanceof Error ? error.message : String(error);

        stepResults.push({
          stepId: step.id,
          command: step.command,
          status: "error",
          duration,
          error: errorMessage,
        });

        postMessage(port, {
          type: "STEP_ERROR",
          stepId: step.id,
          stepIndex: i,
          error: errorMessage,
          duration,
        });

        postMessage(port, {
          type: "EXECUTION_COMPLETE",
          mode,
          success: false,
          stepResults,
        });

        return;
      } finally {
        timeout.cleanup();
        tabClosedReject = null;
      }
    }

    if (!aborted) {
      postMessage(port, {
        type: "EXECUTION_COMPLETE",
        mode,
        success: true,
        stepResults,
      });
    }
  } finally {
    chrome.tabs.onRemoved.removeListener(onTabRemoved);
    port.onDisconnect.removeListener(onDisconnect);
  }
}
