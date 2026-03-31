import { createRoute, useNavigate } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { rootRoute } from "../__root";
import { ScenarioForm } from "../../components/scenarios/scenario-form";
import { useCreateScenario } from "../../lib/hooks/use-scenarios";
import { Button } from "../../components/ui/button";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

export const newScenarioRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/scenarios/new",
  component: NewScenarioPage,
});

function NewScenarioPage() {
  const navigate = useNavigate();
  const createMutation = useCreateScenario();

  const handleSubmit = (data: ScenarioCreate) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        navigate({ to: "/" });
      },
    });
  };

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={() => navigate({ to: "/" })}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h2 className="text-sm font-semibold">New Scenario</h2>
      </div>
      <ScenarioForm
        mode="create"
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending}
      />
    </div>
  );
}
