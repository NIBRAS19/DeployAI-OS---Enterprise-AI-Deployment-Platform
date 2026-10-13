import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { requirements } from "@/lib/mock-data";

const priorityVariant: Record<string, "default" | "info" | "warning" | "destructive"> = {
  Low: "default",
  Medium: "info",
  High: "warning",
  Critical: "destructive",
};

const statusVariant: Record<string, "default" | "info" | "success" | "warning" | "destructive"> = {
  Draft: "default",
  Validated: "info",
  "In Development": "info",
  Testing: "warning",
  Accepted: "success",
  Rejected: "destructive",
};

export default function RequirementsPage() {
  return (
    <div>
      <PageHeader
        title="Requirements"
        description="Functional, non-functional, and compliance requirements gathered during discovery"
      />
      <Card className="overflow-hidden">
        <table className="w-full text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
            <tr>
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Title</th>
              <th className="px-4 py-3 font-medium">Type</th>
              <th className="px-4 py-3 font-medium">Priority</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Stakeholder</th>
            </tr>
          </thead>
          <tbody>
            {requirements.map((r) => (
              <tr key={r.id} className="border-b border-zinc-100 last:border-0">
                <td className="px-4 py-3 font-mono text-xs text-zinc-500">{r.id}</td>
                <td className="px-4 py-3 text-zinc-800">{r.title}</td>
                <td className="px-4 py-3 text-zinc-500">{r.type}</td>
                <td className="px-4 py-3">
                  <Badge variant={priorityVariant[r.priority]}>{r.priority}</Badge>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
                </td>
                <td className="px-4 py-3 text-zinc-500">{r.stakeholder}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
