export interface PickerSelectorResult {
  primary: string;
  alternatives: string[];
}

// --- Content Script → Background → Side Panel (one-shot) ---

export interface PickerResultMessage {
  type: "PICKER_RESULT";
  selectors: PickerSelectorResult;
}

export interface PickerErrorMessage {
  type: "PICKER_ERROR";
  error: string;
}

