import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  // The app build gets JSX from WXT's React module; this standalone config needs
  // its own transform so .test.tsx files compile with the automatic runtime.
  esbuild: { jsx: "automatic" },
  test: {
    globals: true,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    setupFiles: ["src/test/setup-dom.ts"],
    coverage: {
      provider: "v8",
      include: [
        "src/lib/**/*.{ts,tsx}",
        "src/components/scenarios/**/*.tsx",
        "src/entrypoints/background/**/*.ts",
      ],
      exclude: ["src/lib/**/types.ts", "src/test/**"],
      reporter: ["text"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
});
