import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { projects } from "@/lib/mock-data";

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

export default function ProjectsPage() {
  return (
    <div>
      <PageHeader title="Projects" description="AI deployment engagements across all customer organizations" />
      <div className="space-y-3">
        {projects.map((p) => (
          <Link key={p.id} href={`/projects/${p.id}/overview`}>
            <Card className="flex items-center justify-between p-5 transition-colors hover:border-brand-300">
              <div>
                <p className="text-sm font-medium text-zinc-900">{p.name}</p>
                <p className="text-xs text-zinc-400">{p.customerName}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={environmentVariant[p.environment]}>{p.environment}</Badge>
                <Badge variant={statusVariant[p.status]}>{p.status}</Badge>
                <ArrowRight className="h-4 w-4 text-zinc-400" />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
