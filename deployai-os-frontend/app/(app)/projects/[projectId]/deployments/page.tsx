import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { deployments } from "@/lib/mock-data";

const statusVariant: Record<string, "success" | "warning" | "destructive"> = {
  healthy: "success",
  degraded: "warning",
  failed: "destructive",
};

const environments: { id: "production" | "staging" | "development"; label: string }[] = [
  { id: "production", label: "Production" },
  { id: "staging", label: "Staging" },
  { id: "development", label: "Development" },
];

export default function DeploymentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <PageHeader title="Deployments" description="Environment status and release history for this project" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {environments.map((env) => {
            const current = deployments.find((d) => d.environment === env.id);
            return (
              <Card key={env.id} className="p-5">
                <p className="text-sm font-medium text-zinc-900">{env.label}</p>
                {current ? (
                  <>
                    <p className="mt-2 text-xl font-semibold text-zinc-900">{current.version}</p>
                    <div className="mt-2 flex items-center gap-2">
                      <Badge variant={statusVariant[current.status]}>{current.status}</Badge>
                      <span className="text-xs text-zinc-400">{current.deployedAt}</span>
                    </div>
                  </>
                ) : (
                  <p className="mt-2 text-sm text-zinc-400">No pipeline deployments — active development only</p>
                )}
              </Card>
            );
          })}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Deployment History</CardTitle>
          <CardDescription>Every release across all environments</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
              <tr>
                <th className="px-5 py-3 font-medium">Version</th>
                <th className="px-5 py-3 font-medium">Environment</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Deployed By</th>
                <th className="px-5 py-3 font-medium">Deployed At</th>
                <th className="px-5 py-3 font-medium">Commit</th>
                <th className="px-5 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {deployments.map((d) => (
                <tr key={d.id} className="border-b border-zinc-100 last:border-0">
                  <td className="px-5 py-3 font-medium text-zinc-800">{d.version}</td>
                  <td className="px-5 py-3 text-zinc-500">{d.environment}</td>
                  <td className="px-5 py-3">
                    <Badge variant={statusVariant[d.status]}>{d.status}</Badge>
                  </td>
                  <td className="px-5 py-3 text-zinc-500">{d.deployedBy}</td>
                  <td className="px-5 py-3 text-zinc-500">{d.deployedAt}</td>
                  <td className="px-5 py-3 font-mono text-xs text-zinc-400">{d.commit}</td>
                  <td className="px-5 py-3 text-right">
                    <Button variant="outline" size="sm">
                      Rollback
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
