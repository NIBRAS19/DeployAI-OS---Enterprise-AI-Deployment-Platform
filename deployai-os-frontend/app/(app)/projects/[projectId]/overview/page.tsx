import { Check } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { getProject, lifecycleStages } from "@/lib/mock-data";

const architectureLayers = [
  { title: "Client Applications", detail: "Next.js web app, WhatsApp, email" },
  { title: "API Layer", detail: "FastAPI — auth, projects, assistants, workflows" },
  { title: "AI Orchestration", detail: "RAG pipeline, assistant runtime, workflow engine" },
  { title: "Data Layer", detail: "PostgreSQL + pgvector, Redis cache/queue" },
  { title: "External Integrations", detail: "Company systems, email, WhatsApp Business API" },
];

export default function OverviewPage({ params }: { params: { projectId: string } }) {
  const project = getProject(params.projectId);
  const currentIndex = lifecycleStages.findIndex((s) => s.id === project.currentStage);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Project Summary</CardTitle>
          <CardDescription>
            A single AI assistant deployment covering internal knowledge search, support-request routing, and
            approval-gated customer messaging for {project.customerName}.
          </CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Lifecycle Stage</CardTitle>
          <CardDescription>Where this deployment currently sits in the delivery lifecycle</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-start overflow-x-auto pb-2">
            {lifecycleStages.map((stage, i) => {
              const done = i < currentIndex;
              const active = i === currentIndex;
              const leftActive = i > 0 && i <= currentIndex;
              const rightActive = i < lifecycleStages.length - 1 && i < currentIndex;
              return (
                <div key={stage.id} className="flex flex-1 flex-col items-center" style={{ minWidth: 88 }}>
                  <div className="flex w-full items-center">
                    <div className={cn("h-px flex-1", i === 0 ? "opacity-0" : leftActive ? "bg-brand-600" : "bg-zinc-200")} />
                    <div
                      className={cn(
                        "flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border text-xs font-medium",
                        done
                          ? "border-brand-600 bg-brand-600 text-white"
                          : active
                          ? "border-brand-600 bg-white text-brand-700"
                          : "border-zinc-300 bg-white text-zinc-400"
                      )}
                    >
                      {done ? <Check className="h-3.5 w-3.5" /> : i + 1}
                    </div>
                    <div
                      className={cn(
                        "h-px flex-1",
                        i === lifecycleStages.length - 1 ? "opacity-0" : rightActive ? "bg-brand-600" : "bg-zinc-200"
                      )}
                    />
                  </div>
                  <p className={cn("mt-2 text-center text-xs", active ? "font-medium text-brand-700" : "text-zinc-500")}>
                    {stage.label}
                  </p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Architecture at a Glance</CardTitle>
          <CardDescription>High-level system layers for this deployment</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mx-auto flex max-w-md flex-col items-center">
            {architectureLayers.map((layer, i) => (
              <div key={layer.title} className="w-full">
                <div className="rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-3 text-center">
                  <p className="text-sm font-medium text-zinc-900">{layer.title}</p>
                  <p className="text-xs text-zinc-500">{layer.detail}</p>
                </div>
                {i < architectureLayers.length - 1 && (
                  <div className="flex justify-center py-1 text-zinc-300">↓</div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
