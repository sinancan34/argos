import { useState, useCallback, useEffect, useRef } from "react";
import type { PickerSelectorResult } from "@/lib/picker/types";

interface UseElementPickerReturn {
  isPicking: boolean;
  startPicker: (onResult: (result: PickerSelectorResult) => void) => void;
  cancelPicker: () => void;
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

      chrome.runtime.sendMessage({ type: "PICKER_START" }).then((response) => {
        if (response && !response.success) {
          cleanup();
        }
      });
    },
    [isPicking, cleanup],
  );

  const cancelPicker = useCallback(() => {
    if (!isPicking) return;
    chrome.runtime.sendMessage({ type: "PICKER_CANCEL" }).catch(() => {});
    cleanup();
  }, [isPicking, cleanup]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (listenerRef.current) {
        chrome.runtime.sendMessage({ type: "PICKER_CANCEL" }).catch(() => {});
        cleanup();
      }
    };
  }, [cleanup]);

  return { isPicking, startPicker, cancelPicker };
}
