async (el) => {
  // Scrolls the page to `el` as a person does: bursts of wheel notches, or swipes on a touch device,
  // with reading pauses between, until the element's top sits in the band of the viewport people read in.
  // The browser fires real scroll events and IntersectionObserver callbacks along the way.
  // ponytail: scrolls the document only, vertically; an element inside its own scroll container fails
  // with a message, or is left where it is when that container scrolls sideways (a carousel slide).
  // The numbers are starting values: tune them against live runs.
  const BAND = [0.15, 0.55];
  // Room for ~30k px of wheel bursts with pauses; stays under the runner's 180 s MCP client timeout.
  const MAX_MS = 60000;
  const FRAME_MS = 16;
  const WHEEL = { notchPx: 100, notches: [3, 8], notchGapMs: [30, 60], pauseMs: [300, 900] };
  const SWIPE = { viewport: [0.4, 0.8], durationMs: [300, 600], pauseMs: [600, 1500] };

  const between = ([low, high]) => low + Math.random() * (high - low);
  const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
  // "instant", so a site's `scroll-behavior: smooth` does not queue the steps up.
  const scrollBy = (top) => window.scrollBy({ top, behavior: "instant" });
  const toward = (distance, most) => Math.sign(distance) * Math.min(Math.abs(distance), most);

  const wheel = async (distance) => {
    const notches = Math.round(between(WHEEL.notches));
    let left = distance;
    for (let notch = 0; notch < notches && Math.abs(left) >= 1; notch++) {
      const step = toward(left, WHEEL.notchPx);
      scrollBy(step);
      left -= step;
      await sleep(between(WHEEL.notchGapMs));
    }
  };

  // A fling: fast at first, slowing to a stop (ease-out cubic).
  const swipe = async (distance) => {
    const total = toward(distance, between(SWIPE.viewport) * innerHeight);
    const duration = between(SWIPE.durationMs);
    const start = performance.now();
    let moved = 0;
    for (let t = 0; t < 1; ) {
      await sleep(FRAME_MS);
      t = Math.min(1, (performance.now() - start) / duration);
      const next = Math.round(total * (1 - (1 - t) ** 3));
      scrollBy(next - moved);
      moved = next;
    }
  };

  const gesture = navigator.maxTouchPoints > 0 ? swipe : wheel;
  const pauseMs = navigator.maxTouchPoints > 0 ? SWIPE.pauseMs : WHEEL.pauseMs;
  const started = performance.now();
  while (performance.now() - started < MAX_MS) {
    if (!el.isConnected) throw new Error("custom_scroll: the element left the page while scrolling");
    const { top, bottom } = el.getBoundingClientRect();
    if (top >= BAND[0] * innerHeight && top <= BAND[1] * innerHeight) return true;
    const before = scrollY;
    await gesture(top - between(BAND) * innerHeight);
    if (scrollY === before) {
      // The page ends before the element reaches the band; a person stops here too if they can see it.
      if (bottom > 0 && top < innerHeight) return true;
      throw new Error(`custom_scroll: the page stopped scrolling ${Math.round(top)}px from the element`);
    }
    await sleep(between(pauseMs));
  }
  throw new Error(`custom_scroll: the element was not in view after ${MAX_MS / 1000}s of scrolling`);
}
