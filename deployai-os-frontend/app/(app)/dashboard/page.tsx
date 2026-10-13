import { Users, FolderKanban, Rocket, Bot, Plug, Wrench } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SimpleLineChart } from "@/components/charts/simple-line-chart";
import {
  dashboardSummary,
  aiRequestsTrend,
  recentDeployments,
  failedWorkflows,
  securityEvents,
} from "@/lib/mock-data";

const deploymentStatusVariant: Record<string, "success" | "warning" | "destructive"> = {
  healthy: "success",
  degraded: "warning",
  failed: "destructive",
};

const severityVariant: Record<string, "warning" | "destructive" | "default"> = {
  high: "destructive",
  medium: "warning",
  low: "default",
};

export default function DashboardPage() {
  return (
    <div>
      <PageHeader title="Dashboard" description="Portfolio-wide view across all customer deployments" />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <StatCard label="Active Customers" value={dashboardSummary.activeCustomers.toString()} icon={Users} />
        <StatCard label="Active Projects" value={dashboardSummary.activeProjects.toString()} icon={FolderKanban} />
        <StatCard
          label="Production Deployments"
          value={dashboardSummary.productionDeployments.toString()}
          icon={Rocket}
        />
        <StatCard
          label="AI Requests (7d)"
          value={dashboardSummary.aiRequests.toLocaleString()}
          icon={Bot}
          trend="+8.2% vs prior week"
        />
        <StatCard label="Integration Health" value={`${dashboardSummary.integrationHealth}%`} icon={Plug} />
        <StatCard
          label="Pending Improvements"
          value={dashboardSummary.pendingImprovements.toString()}
          icon={Wrench}
        />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>AI Request Volume</CardTitle>
            <CardDescription>Requests across all production assistants, last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleLineChart data={aiRequestsTrend} xKey="day" yKey="requests" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Deployments</CardTitle>
            <CardDescription>Latest releases across environments</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentDeployments.map((d) => (
              <div
                key={d.id}
                className="flex items-center justify-between border-t border-zinc-100 pt-3 first:border-0 first:pt-0"
              >
                <div>
                  <p className="text-sm font-medium text-zinc-900">{d.version}</p>
                  <p className="text-xs text-zinc-400">
                    {d.deployedBy} · {d.deployedAt}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <Badge variant="outline">{d.environment}</Badge>
                  <Badge variant={deploymentStatusVariant[d.status]}>{d.status}</Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Failed Workflow Runs</CardTitle>
            <CardDescription>Needs attention</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {failedWorkflows.map((f) => (
              <div
                key={f.id}
                className="flex items-center justify-between border-t border-zinc-100 pt-3 first:border-0 first:pt-0"
              >
                <div>
                  <p className="text-sm font-medium text-zinc-900">{f.workflow}</p>
                  <p className="text-xs text-zinc-500">{f.reason}</p>
                </div>
                <span className="text-xs text-zinc-400">{f.when}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Security Events</CardTitle>
            <CardDescription>Cross-tenant and access-control monitoring</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {securityEvents.map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between border-t border-zinc-100 pt-3 first:border-0 first:pt-0"
              >
                <div className="flex items-center gap-2">
                  <Badge variant={severityVariant[s.severity]}>{s.severity}</Badge>
                  <p className="text-sm text-zinc-700">{s.label}</p>
                </div>
                <span className="text-xs text-zinc-400">{s.when}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
