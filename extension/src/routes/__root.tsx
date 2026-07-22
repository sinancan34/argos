import { createRootRoute, Outlet, Link } from "@tanstack/react-router";

export const rootRoute = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-12 w-full max-w-5xl items-center px-4">
          <Link to="/" className="text-base font-semibold tracking-tight">
            Argos
          </Link>
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl p-3">
        <Outlet />
      </main>
    </div>
  );
}
