import { finder } from "@medv/finder";

export interface SelectorResult {
  primary: string;
  alternatives: string[];
}

export function generateSelectors(
  target: Element,
  _doc: Document = document,
): SelectorResult {
  // Walk up from SVG elements to nearest HTMLElement
  let element: Element | null = target;
  while (element && !(element instanceof HTMLElement)) {
    element = element.parentElement;
  }
  if (!element) {
    return { primary: target.tagName.toLowerCase(), alternatives: [] };
  }

  try {
    const primary = finder(element, {
      timeoutMs: 2000,
      seedMinLength: 1,
      optimizedMinLength: 2,
    });
    return { primary, alternatives: [] };
  } catch {
    return { primary: element.tagName.toLowerCase(), alternatives: [] };
  }
}
