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
import type { ScenarioResponse, Step, Validation } from "../../lib/schemas/scenario";
import type { ValidationResult } from "../../lib/executor/types";

type StepStatus = "pending" | "running" | "success" | "error";

interface StepState {
  id: string;
  command: string;
  status: StepStatus;
  duration?: number;
  error?: string;
}

type ValidationStatus = "pending" | "checking" | "pass" | "fail";

interface ValidationState {
  id: string;
  status: ValidationStatus;
  result?: ValidationResult;
}

type ExecutionStatus = "loading" | "running" | "validating" | "completed" | "error";

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
  const [validationStates, setValidationStates] = useState<ValidationState[]>([]);
  const [validationWaiting, setValidationWaiting] = useState(false);
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
    setValidationStates([]);
    setValidationWaiting(false);
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

        const validations = (envelope.data.validations as Validation[]) ?? [];

        setStepStates(
          steps.map((s) => ({
            id: s.id,
            command: s.command,
            status: "pending" as StepStatus,
          })),
        );

        if (validations.length > 0) {
          setValidationStates(
            validations.map((v) => ({
              id: v.id,
              status: "pending" as ValidationStatus,
            })),
          );
        }

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
            case "VALIDATION_PHASE_START":
              setStatus("validating");
              setValidationWaiting(true);
              break;
            case "VALIDATION_WAIT_COMPLETE":
              setValidationWaiting(false);
              break;
            case "VALIDATION_RESULT":
              setValidationStates((prev) =>
                prev.map((v, i) =>
                  i === message.validationIndex
                    ? {
                        ...v,
                        status: message.result.status,
                        result: message.result,
                      }
                    : v,
                ),
              );
              break;
            case "EXECUTION_COMPLETE":
              setStatus("completed");
              setSuccess(message.success);
              if (message.validationResults) {
                setValidationStates(
                  message.validationResults.map((r) => ({
                    id: r.validationId,
                    status: r.status,
                    result: r,
                  })),
                );
              }
              disconnectRef.current = null;
              break;
          }
        };

        const handleDisconnect = () => {
          if (cancelled) return;
          disconnectRef.current = null;
          setStatus((prev) => {
            if (prev === "running" || prev === "validating") {
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
          validations,
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

  const validationIcon = (s: ValidationStatus) => {
    switch (s) {
      case "pending":
        return <Circle className="h-3.5 w-3.5 text-muted-foreground" />;
      case "checking":
        return <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-500" />;
      case "pass":
        return <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />;
      case "fail":
        return <XCircle className="h-3.5 w-3.5 text-destructive" />;
    }
  };

  const passedValidations = validationStates.filter((v) => v.status === "pass").length;
  const failedSteps = stepStates.filter((s) => s.status === "error").length;

  const summaryText = () => {
    if (!isFinished || status !== "completed") return null;

    const stepPart = failedSteps > 0
      ? `${failedSteps} adım başarısız`
      : `${stepStates.length} adım başarılı`;

    if (validationStates.length === 0) {
      return failedSteps > 0 ? `${stepPart}.` : `${stepStates.length} adımın tamamı başarılı.`;
    }

    const valPart = `${passedValidations}/${validationStates.length} doğrulama geçti`;
    return `${stepPart}, ${valPart}.`;
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent showCloseButton={false} className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-sm">
            {isFinished
              ? success
                ? "Tamamlandı"
                : "Başarısız"
              : status === "validating"
                ? "Doğrulanıyor"
                : "Çalıştırılıyor"}
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

          {/* Validation section */}
          {(validationStates.length > 0 || validationWaiting) && (
            <>
              <div className="border-t my-2" />

              {validationWaiting && (
                <div className="flex items-center gap-2 py-1 text-xs text-muted-foreground">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Ağ istekleri bekleniyor...
                </div>
              )}

              {!validationWaiting &&
                validationStates.map((v, i) => (
                  <div key={v.id} className="flex items-start gap-2 text-xs">
                    <span className="mt-0.5 shrink-0">
                      {validationIcon(v.status)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <span className="font-medium">
                        Doğrulama {i + 1}
                      </span>
                      {v.result && !v.result.urlCheckPassed && (
                        <p className="text-destructive mt-0.5 break-words">
                          Eşleşen istek bulunamadı
                        </p>
                      )}
                      {v.result && v.result.urlCheckPassed && v.result.paramResults.length > 0 && (
                        <div className="mt-0.5 space-y-0.5">
                          {v.result.paramResults.map((pr) => (
                            <p
                              key={pr.key}
                              className={`break-words ${pr.passed ? "text-muted-foreground" : "text-destructive"}`}
                            >
                              {pr.passed ? "✓" : "✗"} {pr.key}
                              {pr.expected !== undefined && ` (beklenen: ${pr.expected})`}
                              {!pr.passed && pr.actual !== undefined && ` → ${pr.actual}`}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
            </>
          )}
        </div>

        {isFinished && status === "completed" && (
          <div
            className={`text-xs font-medium ${success ? "text-green-600" : "text-destructive"}`}
          >
            {summaryText()}
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
