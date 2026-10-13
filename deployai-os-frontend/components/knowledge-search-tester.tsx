"use client";

import { useState } from "react";
import { Search, FileText, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ResultChunk {
  document: string;
  section: string;
  snippet: string;
  score: number;
}

interface SearchResult {
  restricted: boolean;
  chunks: ResultChunk[];
}

function runMockRetrieval(query: string): SearchResult {
  const q = query.toLowerCase();

  if (q.includes("leave") || q.includes("vacation") || q.includes("pto")) {
    return {
      restricted: false,
      chunks: [
        { document: "Annual_Leave_Policy.pdf", section: "Section 2 — Requesting Leave", snippet: "Employees submit leave requests through the HR portal at least 5 business days in advance for manager approval.", score: 0.93 },
        { document: "Employee_Handbook_v3.pdf", section: "Section 6.1 — Time Off", snippet: "Full-time staff accrue 22 days of annual leave per year, prorated for partial years of service.", score: 0.81 },
      ],
    };
  }

  if (q.includes("travel") || q.includes("reimburs") || q.includes("expense")) {
    return {
      restricted: false,
      chunks: [
        { document: "Travel_and_Expense_Policy.pdf", section: "Section 3 — Reimbursable Expenses", snippet: "Reasonable travel, lodging, and meal expenses are reimbursed within 15 business days of an approved claim.", score: 0.95 },
        { document: "Travel_and_Expense_Policy.pdf", section: "Section 4 — Submission Process", snippet: "Claims must include itemized receipts and be submitted through the finance portal within 30 days of travel.", score: 0.79 },
      ],
    };
  }

  if (q.includes("salary") || q.includes("compensation") || q.includes("executive")) {
    return { restricted: true, chunks: [] };
  }

  return {
    restricted: false,
    chunks: [
      { document: "Support_FAQ_Master.pdf", section: "General", snippet: "This is a demo retrieval — try asking about leave policy or travel reimbursement to see a fuller example.", score: 0.52 },
    ],
  };
}

export function KnowledgeSearchTester() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);

  function handleSearch() {
    if (!query.trim()) return;
    setResult(runMockRetrieval(query));
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Ask a question, e.g. what is our travel reimbursement policy?"
            className="w-full rounded-lg border border-zinc-200 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <Button onClick={handleSearch}>Test retrieval</Button>
      </div>

      {result && (
        <div className="rounded-lg border border-zinc-200 bg-white p-4">
          {result.restricted ? (
            <div className="flex items-start gap-3 text-sm">
              <ShieldAlert className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
              <div>
                <p className="font-medium text-zinc-900">Access denied before retrieval</p>
                <p className="mt-1 text-zinc-500">
                  Matching documents are classified Restricted. The demo user&#39;s role does not have permission, so no chunks were retrieved — authorization runs before the vector search, not after.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-zinc-400">{result.chunks.length} ranked chunks</p>
              {result.chunks.map((chunk, i) => (
                <div key={i} className="flex items-start gap-3 border-t border-zinc-100 pt-3 first:border-0 first:pt-0">
                  <FileText className="mt-0.5 h-4 w-4 flex-shrink-0 text-brand-600" />
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-sm font-medium text-zinc-900">
                      {chunk.document}
                      <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs font-normal text-zinc-500">{chunk.score.toFixed(2)}</span>
                    </div>
                    <p className="text-xs text-zinc-400">{chunk.section}</p>
                    <p className="mt-1 text-sm text-zinc-600">{chunk.snippet}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
