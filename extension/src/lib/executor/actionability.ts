function findElement(selector: string): HTMLElement | null {
  const element = document.querySelector(selector);
  return element instanceof HTMLElement ? element : null;
}

function isVisible(el: HTMLElement): boolean {
  if (el.offsetParent === null && getComputedStyle(el).position !== "fixed") {
    return false;
  }

  const style = getComputedStyle(el);
  if (style.visibility === "hidden" || style.display === "none") {
    return false;
  }

  if (parseFloat(style.opacity) === 0) {
    return false;
  }

  return true;
}

interface Rect {
  readonly top: number;
  readonly left: number;
  readonly width: number;
  readonly height: number;
}

function rectsEqual(a: Rect, b: Rect): boolean {
  return (
    a.top === b.top &&
    a.left === b.left &&
    a.width === b.width &&
    a.height === b.height
  );
}

function isClickable(el: HTMLElement): boolean {
  const rect = el.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;

  const topEl = document.elementFromPoint(centerX, centerY);
  if (!topEl) return false;

  return el === topEl || el.contains(topEl);
}

function waitForDomPresence(
  selector: string,
  deadline: number,
): Promise<HTMLElement> {
  const existing = findElement(selector);
  if (existing) return Promise.resolve(existing);

  return new Promise<HTMLElement>((resolve, reject) => {
    const observer = new MutationObserver(() => {
      const el = findElement(selector);
      if (el) {
        observer.disconnect();
        clearTimeout(timerId);
        resolve(el);
      }
    });

    const timerId = setTimeout(() => {
      observer.disconnect();
      reject(
        new Error(
          `Element not found in DOM within timeout: ${selector}`,
        ),
      );
    }, Math.max(0, deadline - Date.now()));

    observer.observe(document.body, { childList: true, subtree: true });

    // Re-check after observer is attached to avoid race condition
    const el = findElement(selector);
    if (el) {
      observer.disconnect();
      clearTimeout(timerId);
      resolve(el);
    }
  });
}

type ActionabilityPhase =
  | "visibility"
  | "stability"
  | "clickability";

function phaseErrorMessage(phase: ActionabilityPhase): string {
  switch (phase) {
    case "visibility":
      return "Element found but not visible within timeout";
    case "stability":
      return "Element not stable (still animating) within timeout";
    case "clickability":
      return "Element obstructed by another element within timeout";
  }
}

export function waitForActionable(
  selector: string,
  timeout: number,
): Promise<HTMLElement> {
  const deadline = Date.now() + timeout;

  return waitForDomPresence(selector, deadline).then((el) => {
    return new Promise<HTMLElement>((resolve, reject) => {
      let phase: ActionabilityPhase = "visibility";
      let prevRect: Rect | null = null;

      function check(): void {
        if (Date.now() > deadline) {
          reject(new Error(phaseErrorMessage(phase)));
          return;
        }

        switch (phase) {
          case "visibility":
            if (isVisible(el)) {
              el.scrollIntoView({ block: "center", behavior: "instant" });
              phase = "stability";
              prevRect = null;
            }
            break;

          case "stability": {
            const rect = el.getBoundingClientRect();
            const current: Rect = {
              top: rect.top,
              left: rect.left,
              width: rect.width,
              height: rect.height,
            };
            if (prevRect && rectsEqual(prevRect, current)) {
              phase = "clickability";
            }
            prevRect = current;
            break;
          }

          case "clickability":
            if (isClickable(el)) {
              resolve(el);
              return;
            }
            break;
        }

        requestAnimationFrame(check);
      }

      requestAnimationFrame(check);
    });
  });
}
