import { CheckCircle2, ShieldCheck, Quote, Timer } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { evaluationRuns } from "@/lib/mock-data";

export default function EvaluationsPage() {
  const latest = evaluationRuns[evaluationRuns.length - 1];

  return (
    <div className="space-y-6">
      <div>
        <PageHeader
          title="Evaluations"
          description={`Latest automated evaluation run — ${latest.version}, ${latest.date}`}
        />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Correctness" value={`${latest.correctness}%`} icon={CheckCircle2} />
          <StatCard label="Faithfulness" value={`${latest.faithfulness}%`} icon={ShieldCheck} />
          <StatCard label="Citation Accuracy" value={`${latest.citationAccuracy}%`} icon={Quote} />
          <StatCard label="Avg Latency" value={`${latest.avgLatency}s`} icon={Timer} />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Evaluation History</CardTitle>
          <CardDescription>Quality trend across model and prompt iterations</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
              <tr>
                <th className="px-5 py-3 font-medium">Version</th>
                <th className="px-5 py-3 font-medium">Date</th>
                <th className="px-5 py-3 font-medium">Correctness</th>
                <th className="px-5 py-3 font-medium">Faithfulness</th>
                <th className="px-5 py-3 font-medium">Citation Accuracy</th>
                <th className="px-5 py-3 font-medium">Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              {evaluationRuns.map((run) => (
                <tr key={run.id} className="border-b border-zinc-100 last:border-0">
                  <td className="px-5 py-3 font-medium text-zinc-800">{run.version}</td>
                  <td className="px-5 py-3 text-zinc-500">{run.date}</td>
                  <td className="px-5 py-3 text-zinc-500">{run.correctness}%</td>
                  <td className="px-5 py-3 text-zinc-500">{run.faithfulness}%</td>
                  <td className="px-5 py-3 text-zinc-500">{run.citationAccuracy}%</td>
                  <td className="px-5 py-3 text-zinc-500">{run.avgLatency}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
