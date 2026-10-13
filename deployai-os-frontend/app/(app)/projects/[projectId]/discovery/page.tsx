import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const discoveryItems = [
  {
    title: "Business Goal",
    body: "Reduce time spent by staff searching internal policy documents and routing routine support questions, while keeping sensitive company data access tightly controlled.",
  },
  {
    title: "Current Process",
    body: "Employees email HR or Ops directly for policy questions; support requests arrive by email and WhatsApp and are triaged manually each morning.",
  },
  {
    title: "Pain Points",
    body: "Slow response times on common questions, inconsistent answers between staff, no audit trail of who accessed sensitive HR/finance documents.",
  },
  {
    title: "Users",
    body: "Roughly 340 employees across HR, Finance, Operations and Support; a small admin group manages the assistant configuration and reviews outbound messages.",
  },
  {
    title: "Existing Systems",
    body: "PostgreSQL-backed CRM and HR/Ops databases, a document repository for policies, a shared support inbox, and a WhatsApp Business number for customer support.",
  },
  {
    title: "Constraints",
    body: "No new infrastructure spend beyond the existing PostgreSQL instance; must run within GulfBridge's existing security review process; launch within one quarter.",
  },
  {
    title: "Security Requirements",
    body: "Document-level access control by classification (Public / Internal / Confidential / Restricted), full audit logging, and human approval before any outbound customer message.",
  },
  {
    title: "Success Metrics",
    body: "Cut average time-to-answer for policy questions, reach 90%+ positive feedback on assistant responses, and zero unauthorized access to Restricted documents.",
  },
];

const timeline = [
  { label: "Kickoff & goal alignment", when: "Week 1" },
  { label: "Stakeholder interviews (HR, Finance, Ops, Support)", when: "Week 1–2" },
  { label: "Existing systems & data audit", when: "Week 2" },
  { label: "Requirements drafted & reviewed", when: "Week 3" },
  { label: "Requirements sign-off", when: "Week 3" },
];

export default function DiscoveryPage() {
  return (
    <div>
      <PageHeader
        title="Discovery"
        description="Findings from stakeholder interviews and systems review at engagement kickoff"
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {discoveryItems.map((item) => (
          <Card key={item.title}>
            <CardHeader>
              <CardTitle>{item.title}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-zinc-600">{item.body}</CardContent>
          </Card>
        ))}
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Discovery Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-0">
            {timeline.map((t, i) => (
              <div key={t.label} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="h-2.5 w-2.5 flex-shrink-0 rounded-full bg-brand-600" />
                  {i < timeline.length - 1 && <div className="w-px flex-1 bg-zinc-200" />}
                </div>
                <div className="pb-5">
                  <p className="text-sm font-medium text-zinc-900">{t.label}</p>
                  <p className="text-xs text-zinc-400">{t.when}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
