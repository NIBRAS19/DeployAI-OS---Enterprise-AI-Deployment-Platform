import { MessageSquare, ThumbsUp, ThumbsDown } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SimpleBarChart } from "@/components/charts/simple-bar-chart";
import { feedbackBreakdown, feedbackEntries } from "@/lib/mock-data";

export default function FeedbackPage() {
  return (
    <div>
      <PageHeader title="Feedback" description="How employees are rating assistant responses" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Total Responses Rated"
          value={feedbackBreakdown.totalResponses.toLocaleString()}
          icon={MessageSquare}
        />
        <StatCard label="Positive" value={`${feedbackBreakdown.positivePct}%`} icon={ThumbsUp} />
        <StatCard label="Negative" value={`${feedbackBreakdown.negativePct}%`} icon={ThumbsDown} />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Issues Behind Negative Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleBarChart data={feedbackBreakdown.topIssues} xKey="label" yKey="count" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Feedback</CardTitle>
            <CardDescription>Latest rated responses</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {feedbackEntries.map((f) => (
              <div key={f.id} className="border-t border-zinc-100 pt-3 first:border-0 first:pt-0">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm text-zinc-800">{f.question}</p>
                  <Badge variant={f.sentiment === "positive" ? "success" : "destructive"}>{f.sentiment}</Badge>
                </div>
                <div className="mt-1 flex items-center gap-2 text-xs text-zinc-400">
                  {f.reason && <span>{f.reason} ·</span>}
                  <span>{f.createdAt}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
