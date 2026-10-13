import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { auditLogs } from "@/lib/mock-data";

export default function AuditPage() {
  return (
    <div>
      <PageHeader title="Audit Log" description="Immutable record of configuration changes and access events" />
      <Card className="overflow-hidden">
        <table className="w-full text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
            <tr>
              <th className="px-4 py-3 font-medium">Timestamp</th>
              <th className="px-4 py-3 font-medium">Actor</th>
              <th className="px-4 py-3 font-medium">Action</th>
              <th className="px-4 py-3 font-medium">Resource</th>
              <th className="px-4 py-3 font-medium">IP Address</th>
            </tr>
          </thead>
          <tbody>
            {auditLogs.map((log) => (
              <tr key={log.id} className="border-b border-zinc-100 last:border-0">
                <td className="px-4 py-3 font-mono text-xs text-zinc-500">{log.timestamp}</td>
                <td className="px-4 py-3 text-zinc-600">{log.actor}</td>
                <td className="px-4 py-3">
                  <span className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-xs text-zinc-600">
                    {log.action}
                  </span>
                </td>
                <td className="px-4 py-3 text-zinc-500">
                  {log.resourceType}/{log.resourceId}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-zinc-400">{log.ipAddress}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
