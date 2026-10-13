import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { ProjectTabs } from "@/components/project-tabs";
import { getProject } from "@/lib/mock-data";

const environmentVariant: Record<string, "success" | "info" | "warning"> = {
  production: "success",
  staging: "info",
  development: "warning",
};

const statusVariant: Record<string, "success" | "warning" | "default"> = {
  active: "success",
  paused: "warning",
  completed: "default",
};

export default function ProjectLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: { projectId: string };
}) {
  const project = getProject(params.projectId);

  return (
    <div className="-m-6">
      <div className="border-b border-zinc-200 bg-white px-6 py-5">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-zinc-900">{project.name}</h1>
          <Badge variant={environmentVariant[project.environment]}>{project.environment}</Badge>
          <Badge variant={statusVariant[project.status]}>{project.status}</Badge>
        </div>
        <p className="mt-1 text-sm text-zinc-500">{project.customerName}</p>
      </div>
      <ProjectTabs projectId={params.projectId} />
      <div className="p-6">{children}</div>
    </div>
  );
}
