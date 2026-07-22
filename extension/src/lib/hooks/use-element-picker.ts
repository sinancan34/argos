import { useState, useCallback, useEffect, useRef } from "react";
import type {
  PickerCancelMessage,
  PickerSelectorResult,
  PickerStartMessage,
} from "@/lib/picker/types";

interface UseElementPickerReturn {
  isPicking: boolean;
  startPicker: (onResult: (result: PickerSelectorResult) => void) => void;
  cancelPicker: () => void;
}

/**
 * The tab DevTools is attached to. Only defined inside a DevTools page, which
 * is the sole surface hosting this UI.
 */
const CANCEL_MESSAGE: PickerCancelMessage = { type: "PICKER_CANCEL" };

function getInspectedTabId(): number | null {
  const tabId = chrome.devtools?.inspectedWindow?.tabId;
  return typeof tabId === "number" ? tabId : null;
}

export function useElementPicker(): UseElementPickerReturn {
  const [isPicking, setIsPicking] = useState(false);
  const callbackRef = useRef<((result: PickerSelectorResult) => void) | null>(null);
  const listenerRef = useRef<((message: { type: string; selectors?: PickerSelectorResult; error?: string }) => void) | null>(null);

  const cleanup = useCallback(() => {
    if (listenerRef.current) {
      chrome.runtime.onMessage.removeListener(listenerRef.current);
      listenerRef.current = null;
    }
    callbackRef.current = null;
    setIsPicking(false);
  }, []);

  const startPicker = useCallback(
    (onResult: (result: PickerSelectorResult) => void) => {
      if (isPicking) return;

      const tabId = getInspectedTabId();
      if (tabId === null) return;

      callbackRef.current = onResult;

      const listener = (message: { type: string; selectors?: PickerSelectorResult; error?: string }) => {
        if (message.type === "PICKER_RESULT" && message.selectors) {
          const cb = callbackRef.current;
          cleanup();
          cb?.(message.selectors);
        } else if (message.type === "PICKER_ERROR") {
          cleanup();
        }
      };

      listenerRef.current = listener;
      chrome.runtime.onMessage.addListener(listener);
      setIsPicking(true);

      const startMessage: PickerStartMessage = { type: "PICKER_START", tabId };
      chrome.runtime.sendMessage(startMessage).then((response) => {
        if (response && !response.success) {
          cleanup();
        }
      });
    },
    [isPicking, cleanup],
  );

  const cancelPicker = useCallback(() => {
    if (!isPicking) return;
    chrome.runtime.sendMessage(CANCEL_MESSAGE).catch(() => {});
    cleanup();
  }, [isPicking, cleanup]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (listenerRef.current) {
        chrome.runtime.sendMessage(CANCEL_MESSAGE).catch(() => {});
        cleanup();
      }
    };
  }, [cleanup]);

  return { isPicking, startPicker, cancelPicker };
}
