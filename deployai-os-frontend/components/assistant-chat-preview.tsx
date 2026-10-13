"use client";

import { useState } from "react";
import { Send, FileText, ShieldAlert, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citation?: { document: string; section: string };
  refused?: boolean;
}

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content: "Hi, I'm the Company Knowledge Assistant. Ask me about company policy or benefits — I'll always cite the source I used.",
  },
];

function mockAssistantReply(input: string): ChatMessage {
  const q = input.toLowerCase();

  if (q.includes("leave") || q.includes("vacation") || q.includes("pto")) {
    return {
      role: "assistant",
      content: "To request annual leave, submit a request through the HR portal at least 5 business days before your intended time off, for your manager's approval. Full-time staff accrue 22 days per year.",
      citation: { document: "Annual_Leave_Policy.pdf", section: "Section 2" },
    };
  }

  if (q.includes("travel") || q.includes("reimburs") || q.includes("expense")) {
    return {
      role: "assistant",
      content: "Travel, lodging, and meal expenses are reimbursed within 15 business days of an approved claim. Submit itemized receipts through the finance portal within 30 days of travel.",
      citation: { document: "Travel_and_Expense_Policy.pdf", section: "Section 3" },
    };
  }

  if (q.includes("salary") || q.includes("compensation") || q.includes("executive")) {
    return {
      role: "assistant",
      content: "I can't share that — executive compensation records are classified Restricted, and your role doesn't have access. I can loop in HR if you have a specific, authorized request.",
      refused: true,
    };
  }

  return {
    role: "assistant",
    content: "I couldn't find a confident answer to that in the connected knowledge base, so I don't want to guess. Try asking about leave policy or travel reimbursement to see a fuller example.",
  };
}

export function AssistantChatPreview() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");

  function handleSend() {
    if (!input.trim()) return;
    const userMessage: ChatMessage = { role: "user", content: input };
    const reply = mockAssistantReply(input);
    setMessages((prev) => [...prev, userMessage, reply]);
    setInput("");
  }

  return (
    <div className="flex h-[420px] flex-col rounded-lg border border-zinc-200 bg-white">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            {m.role === "assistant" && (
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700">
                <Bot className="h-4 w-4" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${m.role === "user" ? "bg-brand-600 text-white" : "bg-zinc-100 text-zinc-800"}`}>
              <p>{m.content}</p>
              {m.citation && (
                <div className="mt-2 flex items-center gap-1.5 border-t border-zinc-200 pt-2 text-xs text-zinc-500">
                  <FileText className="h-3 w-3" />
                  {m.citation.document} · {m.citation.section}
                </div>
              )}
              {m.refused && (
                <div className="mt-2 flex items-center gap-1.5 border-t border-zinc-200 pt-2 text-xs text-amber-700">
                  <ShieldAlert className="h-3 w-3" />
                  Blocked by document-level authorization
                </div>
              )}
            </div>
            {m.role === "user" && (
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-zinc-200 text-zinc-600">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="flex gap-2 border-t border-zinc-200 p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask the assistant something..."
          className="flex-1 rounded-lg border border-zinc-200 px-3 py-2 text-sm outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
        />
        <Button onClick={handleSend} size="icon">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
