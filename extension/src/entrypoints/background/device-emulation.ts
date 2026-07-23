import type { EmulationParams } from "@/lib/devices/emulation-params";

// CDP version negotiated on attach. The Emulation domain used here is stable in 1.3.
const PROTOCOL_VERSION = "1.3";

/**
 * Attach chrome.debugger to the execution tab and drive the CDP Emulation domain
 * so the tab renders as the selected device — the same commands DevTools' Device
 * Toolbar issues. Returns whether emulation was successfully applied; on any
 * failure it detaches and returns false so the run proceeds at the default
 * viewport rather than aborting. Only the Emulation domain is used, so this does
 * not interfere with the tab's chrome.webRequest capture or content injection.
 */
export async function applyDeviceEmulation(
  tabId: number,
  params: EmulationParams,
): Promise<boolean> {
  const target: chrome.debugger.Debuggee = { tabId };

  try {
    await chrome.debugger.attach(target, PROTOCOL_VERSION);
  } catch {
    // Attach failed (e.g. another debugger already owns the tab). Surface the
    // outcome to the panel via the caller's EMULATION_STATUS message instead of
    // failing the run.
    return false;
  }

  try {
    await chrome.debugger.sendCommand(
      target,
      "Emulation.setDeviceMetricsOverride",
      {
        width: params.deviceMetrics.width,
        height: params.deviceMetrics.height,
        deviceScaleFactor: params.deviceMetrics.deviceScaleFactor,
        mobile: params.deviceMetrics.mobile,
      },
    );

    if (params.userAgent) {
      await chrome.debugger.sendCommand(
        target,
        "Emulation.setUserAgentOverride",
        { userAgent: params.userAgent },
      );
    }

    await chrome.debugger.sendCommand(
      target,
      "Emulation.setTouchEmulationEnabled",
      {
        enabled: params.touch.enabled,
        maxTouchPoints: params.touch.maxTouchPoints,
      },
    );

    return true;
  } catch {
    // A CDP command failed after a successful attach — detach so we don't leave
    // the debugger banner up, then report emulation as not applied.
    await detachDeviceEmulation(tabId);
    return false;
  }
}

/**
 * Detach chrome.debugger from the tab, removing the "started debugging this
 * browser" banner. Safe to call unconditionally — a tab that is already gone or
 * was never attached just throws, which we swallow.
 */
export async function detachDeviceEmulation(tabId: number): Promise<void> {
  try {
    await chrome.debugger.detach({ tabId });
  } catch {
    // Tab already closed or debugger not attached — nothing to clean up.
  }
}
