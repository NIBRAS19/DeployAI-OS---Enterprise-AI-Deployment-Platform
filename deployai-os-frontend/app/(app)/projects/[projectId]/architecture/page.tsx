import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { architectureDecisions } from "@/lib/mock-data";

const statusVariant: Record<string, "success" | "info" | "default"> = {
  Accepted: "success",
  Proposed: "info",
  Superseded: "default",
};

export default function ArchitecturePage() {
  return (
    <div>
      <PageHeader title="Architecture Decisions" description="Key technical decisions and the trade-offs behind them" />
      <div className="space-y-4">
        {architectureDecisions.map((adr) => (
          <Card key={adr.id}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle>
                  <span className="mr-2 font-mono text-xs text-zinc-400">{adr.id}</span>
                  {adr.title}
                </CardTitle>
                <Badge variant={statusVariant[adr.status]}>{adr.status}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-xs font-medium uppercase text-zinc-400">Context</p>
                <p className="mt-1 text-zinc-600">{adr.context}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-zinc-400">Decision</p>
                <p className="mt-1 text-zinc-600">{adr.decision}</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-zinc-400">Trade-offs</p>
                <p className="mt-1 text-zinc-600">{adr.tradeoffs}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
