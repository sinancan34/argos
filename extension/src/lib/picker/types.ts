export interface PickerSelectorResult {
  primary: string;
  alternatives: string[];
}

// --- DevTools Panel → Background (one-shot) ---

export interface PickerStartMessage {
  type: "PICKER_START";
  /** Tab the picker overlay is injected into — always the DevTools-inspected tab. */
  tabId: number;
}

export interface PickerCancelMessage {
  type: "PICKER_CANCEL";
}

// --- Content Script → Background → DevTools Panel (one-shot) ---

export interface PickerResultMessage {
  type: "PICKER_RESULT";
  selectors: PickerSelectorResult;
}

export interface PickerErrorMessage {
  type: "PICKER_ERROR";
  error: string;
}

