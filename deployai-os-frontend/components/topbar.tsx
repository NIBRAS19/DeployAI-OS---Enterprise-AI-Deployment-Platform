import { Bell } from "lucide-react";

export function Topbar() {
  return (
    <header className="flex h-14 flex-shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-6">
      <div className="text-sm text-zinc-500">GulfBridge Professional Services</div>
      <div className="flex items-center gap-4">
        <Bell className="h-4 w-4 text-zinc-400" />
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-600 text-xs font-medium text-white">DE</div>
          <span className="text-sm font-medium text-zinc-700">Demo Engineer</span>
        </div>
      </div>
    </header>
  );
}
