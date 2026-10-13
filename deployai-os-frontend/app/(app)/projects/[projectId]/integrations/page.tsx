import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { integrations } from "@/lib/mock-data";

const statusVariant: Record<string, "success" | "default" | "destructive"> = {
  connected: "success",
  disconnected: "default",
  error: "destructive",
};

export default function IntegrationsPage() {
  return (
    <div>
      <PageHeader title="Integrations" description="Connected systems and channels for this deployment" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {integrations.map((item) => (
          <Card key={item.id} className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-900">{item.name}</p>
                <p className="text-xs text-zinc-400">{item.type}</p>
              </div>
              <Badge variant={statusVariant[item.status]}>{item.status}</Badge>
            </div>
            <p className="mt-4 text-xs text-zinc-400">Last sync: {item.lastSync}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
