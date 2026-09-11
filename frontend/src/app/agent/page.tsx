"use client";

import { useState, useRef, useEffect } from "react";
import { api, type AgentResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  actions?: AgentResponse["actions_taken"];
}

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await api.agentChat(text, conversationId);
      setConversationId(res.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.response, actions: res.actions_taken },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Something went wrong: ${e instanceof Error ? e.message : "unknown error"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-screen max-w-3xl flex-col px-6">
      <div className="flex items-baseline justify-between border-b border-edge py-4">
        <h1 className="text-sm font-medium text-ink">Agent</h1>
        <button
          onClick={() => {
            setMessages([]);
            setConversationId(undefined);
          }}
          className="text-xs text-ink-faint hover:text-ink transition-colors"
        >
          New conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-6">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <p className="text-sm text-ink-dim">
                Describe what you need in plain language.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {[
                  "Search for myproject.dev",
                  "List my domains",
                  "Set up DNS for GitHub Pages",
                  "Add an MX record for Google Workspace",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      setInput(suggestion);
                    }}
                    className="rounded-md border border-edge bg-ground-raised px-3 py-1.5 text-xs text-ink-dim hover:text-ink transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 text-sm ${
                  msg.role === "user"
                    ? "bg-focus/10 text-ink"
                    : "bg-ground-raised text-ink-dim"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.actions && msg.actions.length > 0 && (
                  <div className="mt-2 border-t border-edge pt-2">
                    {msg.actions.map((a, j) => (
                      <p key={j} className="font-mono text-xs text-ink-faint">
                        {a.success ? "+" : "x"} {a.tool}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-ground-raised px-4 py-3">
                <span className="inline-block animate-pulse text-sm text-ink-faint">
                  Thinking...
                </span>
              </div>
            </div>
          )}
        </div>
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-edge py-4">
        <div className="flex items-center gap-2 rounded-lg border border-edge bg-ground-raised px-3">
          <span className="font-mono text-xs text-ink-faint select-none">
            &gt;
          </span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask the agent anything..."
            disabled={loading}
            className="flex-1 bg-transparent py-3 text-sm text-ink placeholder:text-ink-faint focus:outline-none disabled:opacity-50"
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="rounded-md bg-focus px-3 py-1.5 text-xs font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-30"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
