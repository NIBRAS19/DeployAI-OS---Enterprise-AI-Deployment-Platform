import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KnowledgeSearchTester } from "@/components/knowledge-search-tester";
import { knowledgeDocuments } from "@/lib/mock-data";

const classificationVariant: Record<string, "default" | "info" | "warning" | "destructive"> = {
  Public: "default",
  Internal: "info",
  Confidential: "warning",
  Restricted: "destructive",
};

const statusVariant: Record<string, "default" | "info" | "success" | "destructive"> = {
  Uploaded: "default",
  Processing: "info",
  Processed: "info",
  Indexed: "success",
  Failed: "destructive",
};

export default function KnowledgePage() {
  return (
    <div className="space-y-6">
      <div>
        <PageHeader title="Knowledge Base" description="Documents indexed for retrieval, with access classification" />
        <Card className="overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
              <tr>
                <th className="px-4 py-3 font-medium">Filename</th>
                <th className="px-4 py-3 font-medium">Department</th>
                <th className="px-4 py-3 font-medium">Classification</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Chunks</th>
              </tr>
            </thead>
            <tbody>
              {knowledgeDocuments.map((doc) => (
                <tr key={doc.id} className="border-b border-zinc-100 last:border-0">
                  <td className="px-4 py-3 font-medium text-zinc-800">{doc.filename}</td>
                  <td className="px-4 py-3 text-zinc-500">{doc.department}</td>
                  <td className="px-4 py-3">
                    <Badge variant={classificationVariant[doc.classification]}>{doc.classification}</Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={statusVariant[doc.status]}>{doc.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-zinc-500">{doc.chunks}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Retrieval Tester</CardTitle>
          <CardDescription>
            Try a question to see which chunks would be retrieved — and how access control is enforced before
            retrieval, not after.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <KnowledgeSearchTester />
        </CardContent>
      </Card>
    </div>
  );
}
