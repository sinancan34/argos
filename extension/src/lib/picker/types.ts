export interface PickerSelectorResult {
  primary: string;
  alternatives: string[];
}

// --- Side Panel → Background (one-shot) ---

export interface PickerStartMessage {
  type: "PICKER_START";
}

export interface PickerCancelMessage {
  type: "PICKER_CANCEL";
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

export type PickerMessage =
  | PickerStartMessage
  | PickerCancelMessage
  | PickerResultMessage
  | PickerErrorMessage;
