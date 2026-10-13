"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const tabs = [
  { href: "overview", label: "Overview" },
  { href: "discovery", label: "Discovery" },
  { href: "requirements", label: "Requirements" },
  { href: "architecture", label: "Architecture" },
  { href: "integrations", label: "Integrations" },
  { href: "data-sources", label: "Data Sources" },
  { href: "knowledge", label: "Knowledge" },
  { href: "assistants", label: "Assistants" },
  { href: "workflows", label: "Workflows" },
  { href: "deployments", label: "Deployments" },
  { href: "monitoring", label: "Monitoring" },
  { href: "feedback", label: "Feedback" },
  { href: "evaluations", label: "Evaluations" },
  { href: "audit", label: "Audit" },
];

export function ProjectTabs({ projectId }: { projectId: string }) {
  const pathname = usePathname();

  return (
    <div className="flex gap-1 overflow-x-auto border-b border-zinc-200 px-6">
      {tabs.map((tab) => {
        const href = `/projects/${projectId}/${tab.href}`;
        const active = pathname === href;
        return (
          <Link
            key={tab.href}
            href={href}
            className={cn(
              "whitespace-nowrap border-b-2 px-3 py-2.5 text-sm font-medium transition-colors",
              active ? "border-brand-600 text-brand-700" : "border-transparent text-zinc-500 hover:text-zinc-800"
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
