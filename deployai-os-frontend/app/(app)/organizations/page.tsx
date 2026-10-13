import { Building2 } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { organizations } from "@/lib/mock-data";

export default function OrganizationsPage() {
  return (
    <div>
      <PageHeader
        title="Organizations"
        description="Customer organizations using DeployAI OS"
        actions={<Button size="sm">New Organization</Button>}
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {organizations.map((org) => (
          <Card key={org.id} className="p-5">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
                <Building2 className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-zinc-900">{org.name}</p>
                <p className="text-xs text-zinc-400">{org.industry}</p>
              </div>
            </div>
            <p className="mt-4 text-xs text-zinc-500">
              {org.activeProjects} active project{org.activeProjects === 1 ? "" : "s"}
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}
