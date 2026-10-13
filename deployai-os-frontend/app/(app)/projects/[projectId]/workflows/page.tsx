import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { workflows } from "@/lib/mock-data";

const workflowSteps = [
  { title: "Trigger", detail: "New WhatsApp message received from a customer" },
  { title: "Classify", detail: "Determine intent and whether the request touches restricted data" },
  { title: "Authorize & Retrieve", detail: "Check document-level access, then retrieve relevant knowledge chunks" },
  { title: "Draft Response", detail: "Assistant drafts a reply grounded in retrieved chunks, with citations" },
  { title: "Confidence Check", detail: "Low-confidence or restricted-topic drafts are flagged for review" },
  { title: "Human Approval", detail: "A human reviewer approves, edits, or rejects the draft before it is sent" },
  { title: "Send Response", detail: "Approved message is sent back to the customer over WhatsApp" },
  { title: "Log & Audit", detail: "Interaction, decision, and reviewer are recorded in the audit trail" },
];

const statusVariant: Record<string, "success" | "warning" | "default"> = {
  active: "success",
  paused: "warning",
  draft: "default",
};

export default function WorkflowsPage() {
  return (
    <div className="space-y-6">
      <div>
        <PageHeader
          title="Workflows"
          description="Example: WhatsApp Customer Response — human-approval-gated outbound messaging"
        />
        <Card>
          <CardContent className="py-5">
            <div className="mx-auto flex max-w-lg flex-col">
              {workflowSteps.map((step, i) => (
                <div key={step.title}>
                  <div className="flex items-start gap-3 rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-3">
                    <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-medium text-white">
                      {i + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-zinc-900">{step.title}</p>
                      <p className="text-xs text-zinc-500">{step.detail}</p>
                    </div>
                  </div>
                  {i < workflowSteps.length - 1 && (
                    <div className="flex justify-center py-1 text-zinc-300">↓</div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Workflows</CardTitle>
          <CardDescription>Automations configured for this deployment</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
              <tr>
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Last Run</th>
                <th className="px-5 py-3 font-medium">Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {workflows.map((w) => (
                <tr key={w.id} className="border-b border-zinc-100 last:border-0">
                  <td className="px-5 py-3 font-medium text-zinc-800">{w.name}</td>
                  <td className="px-5 py-3">
                    <Badge variant={statusVariant[w.status]}>{w.status}</Badge>
                  </td>
                  <td className="px-5 py-3 text-zinc-500">{w.lastRun}</td>
                  <td className="px-5 py-3 text-zinc-500">{w.successRate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
