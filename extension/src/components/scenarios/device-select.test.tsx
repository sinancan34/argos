// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { DeviceResponse } from "../../lib/schemas/device";

const { useDevicesMock, useDeviceMock } = vi.hoisted(() => ({
  useDevicesMock: vi.fn(),
  useDeviceMock: vi.fn(),
}));

vi.mock("../../lib/hooks/use-devices", () => ({
  useDevices: (params: unknown) => useDevicesMock(params),
  useDevice: (id: string) => useDeviceMock(id),
}));

import { DeviceSelect } from "./device-select";

const IPHONE: DeviceResponse = {
  id: "device-iphone",
  name: "iPhone SE",
  status: true,
  meta: {
    type: "phone",
    viewport: { width: 375, height: 667, device_pixel_ratio: 2 },
  },
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
} as DeviceResponse;

const PIXEL: DeviceResponse = {
  id: "device-pixel",
  name: "Pixel 7",
  status: true,
  meta: {
    type: "phone",
    viewport: { width: 412, height: 915, device_pixel_ratio: 2.625 },
  },
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
} as DeviceResponse;

const DESKTOP: DeviceResponse = {
  id: "device-desktop",
  name: "Desktop",
  status: true,
  meta: {},
  created_at: "2026-07-23T13:10:00+00:00",
  updated_at: "2026-07-23T13:10:00+00:00",
} as DeviceResponse;

const DEBOUNCE_MS = 300;

interface ListState {
  devices?: DeviceResponse[];
  isLoading?: boolean;
  isError?: boolean;
}

function primeList({
  devices = [IPHONE, PIXEL],
  isLoading = false,
  isError = false,
}: ListState = {}): void {
  useDevicesMock.mockReturnValue({
    data: { data: devices },
    isLoading,
    isError,
  });
}

function primeSelected(device: DeviceResponse | null = null): void {
  useDeviceMock.mockReturnValue({ data: device ? { data: device } : undefined });
}

function trigger(): HTMLElement {
  return screen.getAllByRole("button")[0];
}

/**
 * The option button for a device in the open list. Queried via the summary text
 * because the trigger shows the selected device's name too, so matching on name
 * alone is ambiguous once a device is selected.
 */
function optionFor(summary: string): HTMLElement {
  const option = screen.getByText(summary).closest("button");
  if (!option) throw new Error(`No option found for summary: ${summary}`);
  return option;
}

/** Query params the component passed to useDevices on its latest render. */
function lastListParams(): Record<string, unknown> {
  const call = useDevicesMock.mock.calls.at(-1);
  if (!call) throw new Error("useDevices was not called");
  return call[0] as Record<string, unknown>;
}

describe("DeviceSelect", () => {
  beforeEach(() => {
    useDevicesMock.mockReset();
    useDeviceMock.mockReset();
    primeList();
    primeSelected(null);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("trigger", () => {
    it("prompts for a selection when no device is chosen", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Assert
      expect(screen.getByText("Select device...")).toBeInTheDocument();
    });

    it("shows the selected device's name from the loaded list", () => {
      // Arrange & Act
      render(<DeviceSelect value={IPHONE.id} onChange={vi.fn()} />);

      // Assert
      expect(screen.getByText("iPhone SE")).toBeInTheDocument();
    });

    it("falls back to the by-id fetch when the device is not in the list", () => {
      // Arrange — e.g. the list is filtered by a search term
      primeList({ devices: [PIXEL] });
      primeSelected(IPHONE);

      // Act
      render(<DeviceSelect value={IPHONE.id} onChange={vi.fn()} />);

      // Assert
      expect(screen.getByText("iPhone SE")).toBeInTheDocument();
    });

    it("prompts for a selection when neither source resolves the id", () => {
      // Arrange
      primeList({ devices: [] });
      primeSelected(null);

      // Act
      render(<DeviceSelect value="missing-device" onChange={vi.fn()} />);

      // Assert
      expect(screen.getByText("Select device...")).toBeInTheDocument();
    });

    it("marks the trigger invalid when the field has an error", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} hasError />);

      // Assert
      expect(trigger()).toHaveAttribute("aria-invalid", "true");
    });

    it("leaves the trigger valid when there is no error", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Assert
      expect(trigger()).not.toHaveAttribute("aria-invalid");
    });

    it("keeps the trigger out of form submission", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Assert
      expect(trigger()).toHaveAttribute("type", "button");
    });

    it("applies an extra class name to the container", () => {
      // Arrange & Act
      const { container } = render(
        <DeviceSelect value="" onChange={vi.fn()} className="w-64" />,
      );

      // Assert
      expect(container.firstChild).toHaveClass("w-64");
    });
  });

  describe("opening the list", () => {
    it("keeps the list closed initially", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Assert
      expect(
        screen.queryByPlaceholderText("Search devices..."),
      ).not.toBeInTheDocument();
    });

    it("opens the list when the trigger is clicked", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(
        screen.getByPlaceholderText("Search devices..."),
      ).toBeInTheDocument();
    });

    it("closes the list when the trigger is clicked again", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      await user.click(trigger());

      // Act
      await user.click(trigger());

      // Assert
      expect(
        screen.queryByPlaceholderText("Search devices..."),
      ).not.toBeInTheDocument();
    });

    it("closes the list on a mousedown outside the component", async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <div>
          <DeviceSelect value="" onChange={vi.fn()} />
          <span data-testid="outside">outside</span>
        </div>,
      );
      await user.click(trigger());

      // Act
      await user.click(screen.getByTestId("outside"));

      // Assert
      expect(
        screen.queryByPlaceholderText("Search devices..."),
      ).not.toBeInTheDocument();
    });

    it("stays open on a mousedown inside the list", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      await user.click(trigger());

      // Act
      await user.click(screen.getByPlaceholderText("Search devices..."));

      // Assert
      expect(
        screen.getByPlaceholderText("Search devices..."),
      ).toBeInTheDocument();
    });
  });

  describe("list contents", () => {
    it("reports the loading state", async () => {
      // Arrange
      primeList({ devices: [], isLoading: true });
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    it("reports a load failure", async () => {
      // Arrange
      primeList({ devices: [], isError: true });
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.getByText("Failed to load devices")).toBeInTheDocument();
    });

    it("reports an empty result set", async () => {
      // Arrange
      primeList({ devices: [] });
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.getByText("No devices found")).toBeInTheDocument();
    });

    it("does not report emptiness while still loading", async () => {
      // Arrange
      primeList({ devices: [], isLoading: true });
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.queryByText("No devices found")).not.toBeInTheDocument();
    });

    it("does not report emptiness when the request failed", async () => {
      // Arrange
      primeList({ devices: [], isError: true });
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.queryByText("No devices found")).not.toBeInTheDocument();
    });

    it("renders an option per device", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.getByRole("button", { name: /Pixel 7/ })).toBeInTheDocument();
    });

    it("shows a viewport summary beside the device name", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(screen.getByText("375×667 · phone")).toBeInTheDocument();
    });

    it("omits the summary for a device with no viewport or type", async () => {
      // Arrange — deviceSummary returns an empty string
      primeList({ devices: [DESKTOP] });
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(
        screen.getByRole("button", { name: "Desktop" }),
      ).toBeInTheDocument();
    });

    it("requests only active devices sorted by name", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Assert
      expect(lastListParams()).toMatchObject({
        status: true,
        sort_by: "name",
        sort_order: "asc",
        size: 100,
      });
    });

    it("sends no name filter before anything is typed", () => {
      // Arrange & Act
      render(<DeviceSelect value="" onChange={vi.fn()} />);

      // Assert
      expect(lastListParams().name).toBeUndefined();
    });

    it("looks up the selected device by id", () => {
      // Arrange & Act
      render(<DeviceSelect value={IPHONE.id} onChange={vi.fn()} />);

      // Assert
      expect(useDeviceMock).toHaveBeenCalledWith(IPHONE.id);
    });
  });

  describe("selecting a device", () => {
    it("reports the chosen device's id", async () => {
      // Arrange
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={onChange} />);
      await user.click(trigger());

      // Act
      await user.click(screen.getByRole("button", { name: /Pixel 7/ }));

      // Assert
      expect(onChange).toHaveBeenCalledWith(PIXEL.id);
    });

    it("closes the list after a selection", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      await user.click(trigger());

      // Act
      await user.click(screen.getByRole("button", { name: /Pixel 7/ }));

      // Assert
      expect(
        screen.queryByPlaceholderText("Search devices..."),
      ).not.toBeInTheDocument();
    });

    it("reports the selection exactly once", async () => {
      // Arrange
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(<DeviceSelect value="" onChange={onChange} />);
      await user.click(trigger());

      // Act
      await user.click(screen.getByRole("button", { name: /Pixel 7/ }));

      // Assert
      expect(onChange).toHaveBeenCalledTimes(1);
    });

    it("highlights the currently selected option", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value={IPHONE.id} onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(optionFor("375×667 · phone")).toHaveClass("bg-accent/50");
    });

    it("does not highlight an unselected option", async () => {
      // Arrange
      const user = userEvent.setup();
      render(<DeviceSelect value={IPHONE.id} onChange={vi.fn()} />);

      // Act
      await user.click(trigger());

      // Assert
      expect(optionFor("412×915 · phone")).not.toHaveClass("bg-accent/50");
    });
  });

  // The debounce is the behavior under test here, so these use fake timers.
  // userEvent's own internals await real timers even with `delay: null`, so
  // fireEvent — which schedules nothing — is the right driver for this group.
  describe("search", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    function searchBox(): HTMLElement {
      return screen.getByPlaceholderText("Search devices...");
    }

    function typeSearch(value: string): void {
      fireEvent.change(searchBox(), { target: { value } });
    }

    async function settleDebounce(): Promise<void> {
      await act(async () => {
        await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);
      });
    }

    it("passes the debounced search term to the query", async () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());

      // Act
      typeSearch("pix");
      await settleDebounce();

      // Assert
      expect(lastListParams().name).toBe("pix");
    });

    it("does not query before the debounce elapses", () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());

      // Act
      typeSearch("pix");

      // Assert
      expect(lastListParams().name).toBeUndefined();
    });

    it("queries only once for a rapid sequence of keystrokes", async () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());

      // Act
      typeSearch("p");
      typeSearch("pi");
      typeSearch("pix");
      await settleDebounce();

      // Assert
      expect(lastListParams().name).toBe("pix");
    });

    it("drops a whitespace-only search term", async () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());

      // Act
      typeSearch("   ");
      await settleDebounce();

      // Assert
      expect(lastListParams().name).toBeUndefined();
    });

    it("trims the search term before querying", async () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());

      // Act
      typeSearch(" pix ");
      await settleDebounce();

      // Assert
      expect(lastListParams().name).toBe("pix");
    });

    it("drops the filter again when the search box is cleared", async () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());
      typeSearch("pix");
      await settleDebounce();

      // Act
      typeSearch("");
      await settleDebounce();

      // Assert
      expect(lastListParams().name).toBeUndefined();
    });

    it("clears the search box after a selection", async () => {
      // Arrange
      render(<DeviceSelect value="" onChange={vi.fn()} />);
      fireEvent.click(trigger());
      typeSearch("pix");
      fireEvent.click(optionFor("412×915 · phone"));

      // Act
      fireEvent.click(trigger());

      // Assert
      expect(searchBox()).toHaveValue("");
    });
  });
});
