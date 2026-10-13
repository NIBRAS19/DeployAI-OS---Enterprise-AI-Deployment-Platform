import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AssistantChatPreview } from "@/components/assistant-chat-preview";
import { assistant } from "@/lib/mock-data";

export default function AssistantsPage() {
  return (
    <div>
      <PageHeader title="Assistants" description="AI assistant configuration and a live preview of its behavior" />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>{assistant.name}</CardTitle>
            <CardDescription>Configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">Model</span>
              <span className="font-mono text-xs text-zinc-700">{assistant.model}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">Temperature</span>
              <span className="text-zinc-700">{assistant.temperature}</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="flex-shrink-0 text-zinc-500">Knowledge base</span>
              <span className="text-right text-zinc-700">{assistant.knowledgeBase}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">Citations</span>
              <Badge variant="info">{assistant.citationMode}</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Live Preview</CardTitle>
            <CardDescription>
              Ask a question the way an employee would — try leave policy, travel expenses, or an
              executive-compensation question
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AssistantChatPreview />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
