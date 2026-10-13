import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { organizations } from "@/lib/mock-data";

const securityRows: { label: string; status: string; variant: "success" | "outline" }[] = [
  { label: "Single sign-on (SSO)", status: "Enabled", variant: "success" },
  { label: "Document-level access control", status: "Enabled", variant: "success" },
  { label: "Human approval for outbound messages", status: "Enabled", variant: "success" },
  { label: "Audit log retention", status: "12 months", variant: "outline" },
];

export default function SettingsPage() {
  const org = organizations[0];

  return (
    <div className="max-w-3xl space-y-6">
      <PageHeader title="Settings" description="Organization, access, and platform configuration" />

      <Card>
        <CardHeader>
          <CardTitle>Organization</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Organization name</Label>
            <Input defaultValue={org.name} readOnly />
          </div>
          <div>
            <Label>Industry</Label>
            <Input defaultValue={org.industry} readOnly />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>Access control and compliance settings for this workspace</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {securityRows.map((row) => (
            <div
              key={row.label}
              className="flex items-center justify-between border-t border-zinc-100 pt-3 first:border-0 first:pt-0"
            >
              <span className="text-sm text-zinc-600">{row.label}</span>
              <Badge variant={row.variant}>{row.status}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>API Access</CardTitle>
          <CardDescription>Keys used by connected systems to call the DeployAI OS API</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2">
            <span className="font-mono text-xs text-zinc-500">sk_live_••••••••••••7f2a</span>
            <Button variant="outline" size="sm">
              Regenerate
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
