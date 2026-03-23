import { useState } from "react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Collapsible } from "radix-ui";
import { ChevronRight, ChevronDown, Trash2, GripVertical } from "lucide-react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { CommandParamsFields } from "./command-params-fields";
import { COMMAND_CATEGORIES } from "../../lib/commands";
import type { ScenarioCreate } from "../../lib/schemas/scenario";

interface StepBuilderProps {
  form: UseFormReturn<ScenarioCreate>;
}

interface SortableStepProps {
  field: { id: string };
  index: number;
  fieldsLength: number;
  form: UseFormReturn<ScenarioCreate>;
  open: boolean;
  onToggle: () => void;
  onRemove: () => void;
}

function SortableStep({
  field,
  index,
  fieldsLength,
  form,
  open,
  onToggle,
  onRemove,
}: SortableStepProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: field.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const command = form.watch(`steps.${index}.command`);

  return (
    <Collapsible.Root
      ref={setNodeRef}
      style={style}
      open={open}
      onOpenChange={onToggle}
      className="rounded-md border bg-card"
    >
      <div className="flex items-center">
        <button
          type="button"
          className="flex cursor-grab items-center self-stretch px-1.5 text-muted-foreground/50 hover:text-muted-foreground active:cursor-grabbing"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="size-3.5" />
        </button>
        <Collapsible.Trigger asChild>
          <button
            type="button"
            className="flex flex-1 items-center gap-1.5 py-3 pr-3 text-left"
          >
            {open ? (
              <ChevronDown className="size-3.5 text-muted-foreground" />
            ) : (
              <ChevronRight className="size-3.5 text-muted-foreground" />
            )}
            <span className="font-mono text-[10px] text-muted-foreground">
              STEP {index + 1}
            </span>
            {!open && command && (
              <span className="font-mono text-[10px] text-muted-foreground">
                · {command}
              </span>
            )}
          </button>
        </Collapsible.Trigger>
      </div>

      <Collapsible.Content className="space-y-2 px-3 pb-3">
        <div>
          <Label className="text-[11px] text-muted-foreground">Command</Label>
          <Select
            value={command}
            onValueChange={(v) =>
              form.setValue(
                `steps.${index}.command`,
                v as ScenarioCreate["steps"][number]["command"],
                { shouldDirty: true },
              )
            }
          >
            <SelectTrigger size="sm" className="mt-0.5 w-full text-xs">
              <SelectValue placeholder="Select command..." />
            </SelectTrigger>
            <SelectContent>
              {COMMAND_CATEGORIES.map((cat) => (
                <SelectGroup key={cat.category}>
                  <SelectLabel>{cat.category}</SelectLabel>
                  {cat.commands.map((cmd) => (
                    <SelectItem
                      key={cmd.command}
                      value={cmd.command}
                      className="text-xs"
                    >
                      {cmd.command}
                    </SelectItem>
                  ))}
                </SelectGroup>
              ))}
            </SelectContent>
          </Select>
          {form.formState.errors.steps?.[index]?.command && (
            <p className="mt-0.5 text-[10px] text-destructive">
              Command is required
            </p>
          )}
        </div>

        <CommandParamsFields form={form} stepIndex={index} />

        {fieldsLength > 1 && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="text-muted-foreground hover:text-destructive"
            onClick={onRemove}
          >
            <Trash2 className="size-3.5" />
            Delete
          </Button>
        )}
      </Collapsible.Content>
    </Collapsible.Root>
  );
}

export function StepBuilder({ form }: StepBuilderProps) {
  const { fields, append, remove, move } = useFieldArray({
    control: form.control,
    name: "steps",
  });

  const [closedItems, setClosedItems] = useState<Set<string>>(new Set());
  const isOpen = (id: string) => !closedItems.has(id);
  const toggleItem = (id: string) => {
    setClosedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor),
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = fields.findIndex((f) => f.id === active.id);
    const newIndex = fields.findIndex((f) => f.id === over.id);
    move(oldIndex, newIndex);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Steps
        </Label>
        <Button
          type="button"
          variant="outline"
          size="xs"
          onClick={() =>
            append({
              id: crypto.randomUUID(),
              command: "" as never,
              params: {},
            })
          }
        >
          + Add Step
        </Button>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={fields.map((f) => f.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-3">
            {fields.map((field, index) => (
              <SortableStep
                key={field.id}
                field={field}
                index={index}
                fieldsLength={fields.length}
                form={form}
                open={isOpen(field.id)}
                onToggle={() => toggleItem(field.id)}
                onRemove={() => remove(index)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {form.formState.errors.steps?.root && (
        <p className="text-[11px] text-destructive">
          At least one step is required
        </p>
      )}
    </div>
  );
}
