import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function StatCard({
  label,
  value,
  icon: Icon,
  trend,
  trendDirection = "up",
}: {
  label: string;
  value: string;
  icon?: LucideIcon;
  trend?: string;
  trendDirection?: "up" | "down";
}) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-zinc-500">{label}</p>
        {Icon && <Icon className="h-4 w-4 text-zinc-400" />}
      </div>
      <p className="mt-2 text-2xl font-semibold text-zinc-900">{value}</p>
      {trend && <p className={cn("mt-1 text-xs", trendDirection === "up" ? "text-emerald-600" : "text-red-600")}>{trend}</p>}
    </Card>
  );
}
