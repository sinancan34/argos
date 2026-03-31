import { createRoute, useNavigate } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { rootRoute } from "../../__root";
import { ScenarioForm } from "../../../components/scenarios/scenario-form";
import {
  useScenario,
  useUpdateScenario,
} from "../../../lib/hooks/use-scenarios";
import { Button } from "../../../components/ui/button";
import type { ScenarioUpdate } from "../../../lib/schemas/scenario";

export const editScenarioRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/scenarios/$scenarioId/edit",
  component: EditScenarioPage,
});

function EditScenarioPage() {
  const { scenarioId } = editScenarioRoute.useParams();
  const navigate = useNavigate();
  const { data, isLoading, error } = useScenario(scenarioId);
  const updateMutation = useUpdateScenario();

  if (isLoading) {
    return <div className="py-8 text-center text-muted-foreground">Loading...</div>;
  }

  if (error || !data) {
    return (
      <div className="py-8 text-center text-destructive">
        Scenario not found
      </div>
    );
  }

  const handleSubmit = (updateData: ScenarioUpdate) => {
    updateMutation.mutate(
      { id: scenarioId, data: updateData },
      {
        onSuccess: () => {
          navigate({ to: "/" });
        },
      },
    );
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
        <h2 className="text-sm font-semibold">Edit Scenario</h2>
      </div>
      <ScenarioForm
        mode="edit"
        defaultValues={data.data}
        onSubmit={handleSubmit}
        isSubmitting={updateMutation.isPending}
      />
    </div>
  );
}
