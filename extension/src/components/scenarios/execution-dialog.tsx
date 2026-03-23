import { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, CheckCircle2, XCircle, Circle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { getScenario } from "../../lib/api/scenarios";
import { connectExecutionPort } from "../../lib/messaging/protocol";
import type { BackgroundMessage } from "../../lib/messaging/types";
import type { ScenarioResponse, Step } from "../../lib/schemas/scenario";

type StepStatus = "pending" | "running" | "success" | "error";

interface StepState {
  id: string;
  command: string;
  status: StepStatus;
  duration?: number;
  error?: string;
}

type ExecutionStatus = "loading" | "running" | "completed" | "error";

interface ExecutionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  scenario: ScenarioResponse | null;
}

export function ExecutionDialog({
  open,
  onOpenChange,
  scenario,
}: ExecutionDialogProps) {
  const [status, setStatus] = useState<ExecutionStatus>("loading");
  const [stepStates, setStepStates] = useState<StepState[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const disconnectRef = useRef<(() => void) | null>(null);

  const cleanup = useCallback(() => {
    if (disconnectRef.current) {
      disconnectRef.current();
      disconnectRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!open || !scenario) return;

    let cancelled = false;

    setStatus("loading");
    setStepStates([]);
    setErrorMessage(null);
    setSuccess(false);

    (async () => {
      try {
        const envelope = await getScenario(scenario.id);
        if (cancelled) return;

        const steps = envelope.data.steps as Step[];

        if (!steps || steps.length === 0) {
          setStatus("error");
          setErrorMessage("Bu senaryoda çalıştırılacak adım yok.");
          return;
        }

        setStepStates(
          steps.map((s) => ({
            id: s.id,
            command: s.command,
            status: "pending" as StepStatus,
          })),
        );
        setStatus("running");

        const handleMessage = (message: BackgroundMessage) => {
          if (cancelled) return;

          switch (message.type) {
            case "STEP_START":
              setStepStates((prev) =>
                prev.map((s, i) =>
                  i === message.stepIndex ? { ...s, status: "running" } : s,
                ),
              );
              break;
            case "STEP_SUCCESS":
              setStepStates((prev) =>
                prev.map((s, i) =>
                  i === message.stepIndex
                    ? { ...s, status: "success", duration: message.duration }
                    : s,
                ),
              );
              break;
            case "STEP_ERROR":
              setStepStates((prev) =>
                prev.map((s, i) =>
                  i === message.stepIndex
                    ? {
                        ...s,
                        status: "error",
                        duration: message.duration,
                        error: message.error,
                      }
                    : s,
                ),
              );
              break;
            case "EXECUTION_COMPLETE":
              setStatus("completed");
              setSuccess(message.success);
              disconnectRef.current = null;
              break;
          }
        };

        const handleDisconnect = () => {
          if (cancelled) return;
          disconnectRef.current = null;
          setStatus((prev) => {
            if (prev === "running") {
              setErrorMessage("Bağlantı kesildi.");
              return "error";
            }
            return prev;
          });
        };

        const { send, disconnect } = connectExecutionPort(
          handleMessage,
          handleDisconnect,
        );
        disconnectRef.current = disconnect;

        send({
          type: "EXECUTE_SCENARIO",
          steps,
          validations: (envelope.data.validations as unknown[]) ?? [],
          stepTimeout: envelope.data.step_timeout,
          validationTimeout: envelope.data.validation_timeout,
        });
      } catch (err) {
        if (cancelled) return;
        setStatus("error");
        setErrorMessage(
          err instanceof Error ? err.message : "Senaryo yüklenirken hata oluştu.",
        );
      }
    })();

    return () => {
      cancelled = true;
      cleanup();
    };
  }, [open, scenario, cleanup]);

  const handleCancel = () => {
    cleanup();
    onOpenChange(false);
  };

  const handleClose = () => {
    cleanup();
    onOpenChange(false);
  };

  const isFinished = status === "completed" || status === "error";

  const stepIcon = (s: StepStatus) => {
    switch (s) {
      case "pending":
        return <Circle className="h-3.5 w-3.5 text-muted-foreground" />;
      case "running":
        return <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-500" />;
      case "success":
        return <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />;
      case "error":
        return <XCircle className="h-3.5 w-3.5 text-destructive" />;
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent showCloseButton={false} className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-sm">
            {isFinished ? (success ? "Tamamlandı" : "Başarısız") : "Çalıştırılıyor"}
          </DialogTitle>
          <DialogDescription className="text-xs truncate">
            {scenario?.name}
          </DialogDescription>
        </DialogHeader>

        <div className="max-h-60 overflow-y-auto space-y-1.5">
          {status === "loading" && (
            <div className="flex items-center gap-2 py-4 justify-center text-xs text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Senaryo yükleniyor...
            </div>
          )}

          {status === "error" && stepStates.length === 0 && errorMessage && (
            <div className="flex items-center gap-2 py-4 justify-center text-xs text-destructive">
              <XCircle className="h-4 w-4" />
              {errorMessage}
            </div>
          )}

          {stepStates.map((step, i) => (
            <div key={step.id} className="flex items-start gap-2 text-xs">
              <span className="mt-0.5 shrink-0">{stepIcon(step.status)}</span>
              <div className="min-w-0 flex-1">
                <span className="font-medium">
                  {i + 1}. {step.command}
                </span>
                {step.duration !== undefined && (
                  <span className="ml-1.5 text-muted-foreground">
                    ({(step.duration / 1000).toFixed(1)}s)
                  </span>
                )}
                {step.error && (
                  <p className="text-destructive mt-0.5 break-words">
                    {step.error}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {isFinished && status === "completed" && (
          <div
            className={`text-xs font-medium ${success ? "text-green-600" : "text-destructive"}`}
          >
            {success
              ? `${stepStates.length} adımın tamamı başarılı.`
              : `${stepStates.filter((s) => s.status === "error").length} adım başarısız.`}
          </div>
        )}

        <DialogFooter>
          {isFinished ? (
            <Button variant="outline" size="sm" className="text-xs" onClick={handleClose}>
              Kapat
            </Button>
          ) : (
            <Button
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={handleCancel}
              disabled={status === "loading"}
            >
              İptal
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
