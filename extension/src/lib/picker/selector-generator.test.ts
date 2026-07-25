// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const { finderMock } = vi.hoisted(() => ({ finderMock: vi.fn() }));

vi.mock("@medv/finder", () => ({
  finder: (element: Element, options: unknown) => finderMock(element, options),
}));

import { generateSelectors } from "./selector-generator";

const actualFinder = await vi.importActual<typeof import("@medv/finder")>(
  "@medv/finder",
);

const EXPECTED_FINDER_OPTIONS = {
  timeoutMs: 2000,
  seedMinLength: 1,
  optimizedMinLength: 2,
};

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

describe("generateSelectors — with the real finder", () => {
  beforeEach(() => {
    finderMock.mockReset();
    finderMock.mockImplementation(actualFinder.finder);
    document.body.innerHTML = "";
  });

  afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
  });

  it("generates a selector that matches the element it was given", () => {
    // Arrange
    const target = document.createElement("button");
    target.id = "buy-now";
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(document.querySelector(primary)).toBe(target);
  });

  it("generates a selector for an element with no id or class", () => {
    // Arrange
    const target = document.createElement("span");
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(document.querySelector(primary)).toBe(target);
  });

  it("distinguishes between sibling elements", () => {
    // Arrange
    const first = document.createElement("li");
    const second = document.createElement("li");
    const list = document.createElement("ul");
    list.append(first, second);
    document.body.appendChild(list);

    // Act
    const { primary } = generateSelectors(second);

    // Assert
    expect(document.querySelector(primary)).toBe(second);
  });

  it("generates a selector for a deeply nested element", () => {
    // Arrange
    document.body.innerHTML = `
      <main><section><article><div><p><a href="#x">link</a></p></div></article></section></main>
    `;
    const target = document.querySelector("a") as HTMLElement;

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(document.querySelector(primary)).toBe(target);
  });

  it("returns no alternatives", () => {
    // Arrange — the current implementation only ever produces a primary
    const target = document.createElement("button");
    document.body.appendChild(target);

    // Act
    const { alternatives } = generateSelectors(target);

    // Assert
    expect(alternatives).toEqual([]);
  });

  it("passes the configured finder options", () => {
    // Arrange
    const target = document.createElement("button");
    document.body.appendChild(target);

    // Act
    generateSelectors(target);

    // Assert
    expect(finderMock).toHaveBeenCalledWith(target, EXPECTED_FINDER_OPTIONS);
  });

  it("calls the finder exactly once", () => {
    // Arrange
    const target = document.createElement("button");
    document.body.appendChild(target);

    // Act
    generateSelectors(target);

    // Assert
    expect(finderMock).toHaveBeenCalledTimes(1);
  });

  it("handles an element whose id contains a Turkish character", () => {
    // Arrange
    const target = document.createElement("button");
    target.id = "ödeme";
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(document.querySelector(primary)).toBe(target);
  });
});

describe("generateSelectors — SVG targets", () => {
  beforeEach(() => {
    finderMock.mockReset();
    finderMock.mockImplementation(actualFinder.finder);
    document.body.innerHTML = "";
  });

  afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
  });

  it("walks up from an SVG child to the nearest HTMLElement", () => {
    // Arrange — an icon inside a button
    const button = document.createElement("button");
    button.id = "icon-button";
    const svg = document.createElementNS(SVG_NAMESPACE, "svg");
    const path = document.createElementNS(SVG_NAMESPACE, "path");
    svg.appendChild(path);
    button.appendChild(svg);
    document.body.appendChild(button);

    // Act
    const { primary } = generateSelectors(path);

    // Assert
    expect(document.querySelector(primary)).toBe(button);
  });

  it("passes the HTMLElement ancestor to the finder, not the SVG node", () => {
    // Arrange
    const button = document.createElement("button");
    const svg = document.createElementNS(SVG_NAMESPACE, "svg");
    button.appendChild(svg);
    document.body.appendChild(button);

    // Act
    generateSelectors(svg);

    // Assert
    expect(finderMock).toHaveBeenCalledWith(button, EXPECTED_FINDER_OPTIONS);
  });

  it("falls back to the tag name for a detached SVG node", () => {
    // Arrange — no HTMLElement ancestor exists
    const circle = document.createElementNS(SVG_NAMESPACE, "circle");

    // Act
    const { primary } = generateSelectors(circle);

    // Assert
    expect(primary).toBe("circle");
  });

  it("does not call the finder when there is no HTMLElement ancestor", () => {
    // Arrange
    const circle = document.createElementNS(SVG_NAMESPACE, "circle");

    // Act
    generateSelectors(circle);

    // Assert
    expect(finderMock).not.toHaveBeenCalled();
  });

  it("returns no alternatives for the detached fallback", () => {
    // Arrange
    const circle = document.createElementNS(SVG_NAMESPACE, "circle");

    // Act
    const { alternatives } = generateSelectors(circle);

    // Assert
    expect(alternatives).toEqual([]);
  });

  it("lowercases the tag name in the fallback", () => {
    // Arrange — SVG tag names are case-sensitive and can be mixed case
    const gradient = document.createElementNS(SVG_NAMESPACE, "linearGradient");

    // Act
    const { primary } = generateSelectors(gradient);

    // Assert
    expect(primary).toBe("lineargradient");
  });
});

describe("generateSelectors — finder failure", () => {
  beforeEach(() => {
    finderMock.mockReset();
    document.body.innerHTML = "";
  });

  afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
  });

  it("falls back to the tag name when the finder throws", () => {
    // Arrange — the finder gives up after its timeout on huge documents
    finderMock.mockImplementation(() => {
      throw new Error("Timeout: unable to find a unique selector");
    });
    const target = document.createElement("button");
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(primary).toBe("button");
  });

  it("returns no alternatives when the finder throws", () => {
    // Arrange
    finderMock.mockImplementation(() => {
      throw new Error("boom");
    });
    const target = document.createElement("div");
    document.body.appendChild(target);

    // Act
    const { alternatives } = generateSelectors(target);

    // Assert
    expect(alternatives).toEqual([]);
  });

  it("does not rethrow the finder's error", () => {
    // Arrange
    finderMock.mockImplementation(() => {
      throw new Error("boom");
    });
    const target = document.createElement("div");
    document.body.appendChild(target);

    // Act & Assert
    expect(() => generateSelectors(target)).not.toThrow();
  });

  it("lowercases the tag name of the fallback", () => {
    // Arrange — HTML tagName is reported uppercase
    finderMock.mockImplementation(() => {
      throw new Error("boom");
    });
    const target = document.createElement("INPUT");
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(primary).toBe("input");
  });

  it("returns whatever selector string the finder produced", () => {
    // Arrange
    finderMock.mockReturnValue("#custom-selector");
    const target = document.createElement("div");
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(primary).toBe("#custom-selector");
  });

  it("passes through an empty selector from the finder without falling back", () => {
    // Arrange — documents that only a throw triggers the fallback
    finderMock.mockReturnValue("");
    const target = document.createElement("div");
    document.body.appendChild(target);

    // Act
    const { primary } = generateSelectors(target);

    // Assert
    expect(primary).toBe("");
  });
});
