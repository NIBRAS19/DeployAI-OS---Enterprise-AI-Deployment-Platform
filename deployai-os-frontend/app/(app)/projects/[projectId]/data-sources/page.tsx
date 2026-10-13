import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { dataSources } from "@/lib/mock-data";

const statusVariant: Record<string, "success" | "default"> = {
  connected: "success",
  disconnected: "default",
};

export default function DataSourcesPage() {
  return (
    <div>
      <PageHeader
        title="Data Sources"
        description="Systems providing data to this deployment's assistants and workflows"
      />
      <Card className="overflow-hidden">
        <table className="w-full text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Kind</th>
              <th className="px-4 py-3 font-medium">Records</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {dataSources.map((d) => (
              <tr key={d.id} className="border-b border-zinc-100 last:border-0">
                <td className="px-4 py-3 font-medium text-zinc-800">{d.name}</td>
                <td className="px-4 py-3 text-zinc-500">{d.kind}</td>
                <td className="px-4 py-3 text-zinc-500">{d.recordCount}</td>
                <td className="px-4 py-3">
                  <Badge variant={statusVariant[d.status]}>{d.status}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
